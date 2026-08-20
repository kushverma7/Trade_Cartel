/**
 * Full AUSIDXAUD 1-minute downloader (2013-2026) using dukascopy-node.
 * Quarter-by-quarter with resume support via manifest JSON.
 */

import { getHistoricalRates } from 'dukascopy-node';
import { writeFileSync, readFileSync, existsSync, mkdirSync, appendFileSync } from 'fs';

const RAW_DIR  = '/home/user/Trade_Cartel/research/au200_10am/data/raw';
const LOG_FILE = '/home/user/Trade_Cartel/research/au200_10am/logs/fetch_all.log';
const MANIFEST = `${RAW_DIR}/manifest.json`;

mkdirSync(RAW_DIR, { recursive: true });
mkdirSync('/home/user/Trade_Cartel/research/au200_10am/logs', { recursive: true });

function log(msg) {
  const s = `${new Date().toISOString()} ${msg}`;
  console.log(s);
  appendFileSync(LOG_FILE, s + '\n');
}

function loadManifest() {
  try { return JSON.parse(readFileSync(MANIFEST, 'utf8')); } catch { return {}; }
}

function saveManifest(m) {
  writeFileSync(MANIFEST, JSON.stringify(m, null, 2));
}

// Build list of (fromDate, toDate, key) chunks
function buildChunks() {
  const chunks = [];
  for (let year = 2013; year <= 2026; year++) {
    const quarters = [
      [`${year}-01-01`, `${year}-04-01`, `${year}_Q1`],
      [`${year}-04-01`, `${year}-07-01`, `${year}_Q2`],
      [`${year}-07-01`, `${year}-10-01`, `${year}_Q3`],
      [`${year}-10-01`, `${year+1}-01-01`, `${year}_Q4`],
    ];
    for (let [from, to, key] of quarters) {
      // Clamp to actual range
      if (from < '2013-01-01') from = '2013-01-01';
      if (to   > '2026-08-20') to   = '2026-08-20';
      if (from >= to) continue;
      chunks.push({ from, to, key });
    }
  }
  return chunks;
}

async function fetchChunk(from, to) {
  return getHistoricalRates({
    instrument: 'ausidxaud',
    dates: { from, to },
    timeframe: 'm1',
    format: 'array',
    batchSize: 150,
    pauseBetweenBatchesMs: 600,
  });
}

async function main() {
  log('=== AUSIDXAUD Full 1-minute Download Start (2013–2026) ===');
  const manifest = loadManifest();
  const chunks   = buildChunks();
  log(`Total chunks: ${chunks.length}`);

  let totalBars = 0;
  let done = 0;

  for (const { from, to, key } of chunks) {
    const outPath = `${RAW_DIR}/ausidxaud_m1_${key}.csv`;

    if (manifest[key] === 'done' && existsSync(outPath)) {
      // Count bars from existing file for logging
      const lines = readFileSync(outPath, 'utf8').split('\n').length - 2; // minus header + trailing newline
      totalBars += Math.max(0, lines);
      done++;
      log(`SKIP ${key} (${lines.toLocaleString()} bars, already done)`);
      continue;
    }

    let attempts = 0;
    while (attempts < 4) {
      try {
        log(`Fetching ${key}: ${from} → ${to}`);
        const data = await fetchChunk(from, to);
        log(`  ${key}: ${data.length.toLocaleString()} bars`);

        // Write CSV
        let csv = 'timestamp_ms,open,high,low,close,volume\n';
        for (const row of data) {
          csv += `${row[0]},${row[1]},${row[2]},${row[3]},${row[4]},${row[5] || 0}\n`;
        }
        writeFileSync(outPath, csv);

        manifest[key] = 'done';
        saveManifest(manifest);
        totalBars += data.length;
        done++;
        log(`  Saved: ${outPath} | Done ${done}/${chunks.length} | Total bars: ${totalBars.toLocaleString()}`);

        // Polite pause between chunks
        await new Promise(r => setTimeout(r, 1500));
        break;

      } catch (err) {
        attempts++;
        const wait = 3000 * Math.pow(2, attempts);
        log(`  ERROR ${key} attempt ${attempts}: ${err.message} — retry in ${wait/1000}s`);
        manifest[key] = `error:${err.message}`;
        saveManifest(manifest);
        await new Promise(r => setTimeout(r, wait));
      }
    }

    if (manifest[key] !== 'done') {
      log(`  FAILED ${key} after ${attempts} attempts — skipping`);
    }
  }

  log(`=== Download complete. ${done}/${chunks.length} chunks, ${totalBars.toLocaleString()} total bars ===`);
}

main().catch(err => { log(`FATAL: ${err}`); process.exit(1); });
