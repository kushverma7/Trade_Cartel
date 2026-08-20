/**
 * AUSIDXAUD 1-minute downloader using dukascopy-node.
 * Downloads year by year, saves to per-year CSV files with resume support.
 *
 * Usage: node fetch_m1.mjs [--start 2013] [--end 2026]
 */

import { getHistoricalRates } from 'dukascopy-node';
import { createWriteStream, existsSync, appendFileSync, readFileSync } from 'fs';
import { mkdirSync } from 'fs';

const RAW_DIR = '/home/user/Trade_Cartel/research/au200_10am/data/raw';
const LOG_FILE = '/home/user/Trade_Cartel/research/au200_10am/logs/fetch_m1.log';
mkdirSync(RAW_DIR, { recursive: true });

const INSTRUMENT = 'ausidxaud';
const START_YEAR = parseInt(process.argv[2] || '2013');
const END_YEAR   = parseInt(process.argv[3] || '2026');

function log(msg) {
  const line = `${new Date().toISOString()} ${msg}`;
  console.log(line);
  appendFileSync(LOG_FILE, line + '\n');
}

function csvPath(year, chunk) {
  return `${RAW_DIR}/ausidxaud_m1_${year}_${String(chunk).padStart(2,'0')}.csv`;
}

function manifestPath() {
  return `${RAW_DIR}/fetch_manifest.json`;
}

function loadManifest() {
  try {
    return JSON.parse(readFileSync(manifestPath(), 'utf8'));
  } catch { return {}; }
}

function saveManifest(m) {
  const { writeFileSync } = await import('fs');
  writeFileSync(manifestPath(), JSON.stringify(m, null, 2));
}

async function downloadChunk(fromDate, toDate, chunkKey) {
  log(`Downloading ${fromDate} → ${toDate}`);

  const data = await getHistoricalRates({
    instrument: INSTRUMENT,
    dates: { from: fromDate, to: toDate },
    timeframe: 'm1',
    format: 'array',
    batchSize: 100,
    pauseBetweenBatchesMs: 800,
  });

  return data;
}

async function main() {
  const manifest = loadManifest();
  log(`=== AUSIDXAUD 1-minute downloader: ${START_YEAR}–${END_YEAR} ===`);

  let totalBars = 0;

  for (let year = START_YEAR; year <= END_YEAR; year++) {
    // Download in 3-month chunks to avoid memory/timeout issues
    const quarters = [
      [`${year}-01-01`, `${year}-04-01`, `${year}_Q1`],
      [`${year}-04-01`, `${year}-07-01`, `${year}_Q2`],
      [`${year}-07-01`, `${year}-10-01`, `${year}_Q3`],
      [`${year}-10-01`, `${year}-12-31`, `${year}_Q4`],
    ];

    for (const [from, to, key] of quarters) {
      const outPath = `${RAW_DIR}/ausidxaud_m1_${key}.csv`;

      // Skip if already downloaded
      if (manifest[key] === 'done' && existsSync(outPath)) {
        log(`  SKIP ${key} (already done)`);
        continue;
      }

      // Clamp dates
      const fromDate = from < '2013-01-02' ? '2013-01-02' : from;
      const toDate   = to   > '2026-08-20' ? '2026-08-20' : to;
      if (fromDate >= toDate) { manifest[key] = 'done'; continue; }

      try {
        const data = await downloadChunk(fromDate, toDate, key);
        log(`  ${key}: ${data.length} bars`);

        // Write CSV
        const ws = createWriteStream(outPath);
        ws.write('timestamp_ms,open,high,low,close,volume\n');
        for (const row of data) {
          ws.write(`${row[0]},${row[1]},${row[2]},${row[3]},${row[4]},${row[5]}\n`);
        }
        ws.end();

        manifest[key] = 'done';
        // Save manifest inline (sync)
        const { writeFileSync } = await import('fs');
        writeFileSync(manifestPath(), JSON.stringify(manifest, null, 2));

        totalBars += data.length;
        log(`  ${key}: saved → ${outPath} (total so far: ${totalBars.toLocaleString()})`);

        // Polite delay between chunks
        await new Promise(r => setTimeout(r, 2000));

      } catch (err) {
        log(`  ERROR ${key}: ${err.message}`);
        manifest[key] = `error:${err.message}`;
        const { writeFileSync } = await import('fs');
        writeFileSync(manifestPath(), JSON.stringify(manifest, null, 2));
        // Wait longer on error before continuing
        await new Promise(r => setTimeout(r, 5000));
      }
    }
  }

  log(`=== Download complete. Total bars: ${totalBars.toLocaleString()} ===`);
}

main().catch(err => { log(`FATAL: ${err.message}`); process.exit(1); });
