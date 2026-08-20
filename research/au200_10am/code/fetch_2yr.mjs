/**
 * AUSIDXAUD 1-minute downloader — 2 years only (2024-08-19 to 2026-08-19)
 */
import { getHistoricalRates } from 'dukascopy-node';
import { writeFileSync, readFileSync, existsSync, mkdirSync, appendFileSync } from 'fs';

const RAW_DIR  = '/home/user/Trade_Cartel/research/au200_10am/data/raw';
const LOG_FILE = '/home/user/Trade_Cartel/research/au200_10am/logs/fetch_2yr.log';
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
function saveManifest(m) { writeFileSync(MANIFEST, JSON.stringify(m, null, 2)); }

// 2 years back from 2026-08-19
const CHUNKS = [
  { from: '2024-08-19', to: '2025-01-01', key: '2024_H2' },
  { from: '2025-01-01', to: '2025-07-01', key: '2025_H1' },
  { from: '2025-07-01', to: '2026-01-01', key: '2025_H2' },
  { from: '2026-01-01', to: '2026-08-20', key: '2026_H1' },
];

async function main() {
  log('=== AUSIDXAUD 2-year download (2024-08-19 → 2026-08-19) ===');
  const manifest = loadManifest();
  let totalBars = 0;

  for (const { from, to, key } of CHUNKS) {
    const outPath = `${RAW_DIR}/ausidxaud_m1_${key}.csv`;

    if (manifest[key] === 'done' && existsSync(outPath)) {
      log(`SKIP ${key} (already done)`);
      continue;
    }

    log(`Fetching ${key}: ${from} → ${to}`);
    let attempts = 0;
    while (attempts < 5) {
      try {
        const data = await getHistoricalRates({
          instrument: 'ausidxaud',
          dates: { from, to },
          timeframe: 'm1',
          format: 'array',
          batchSize: 150,
          pauseBetweenBatchesMs: 600,
        });

        log(`  ${key}: ${data.length.toLocaleString()} bars`);

        let csv = 'timestamp_ms,open,high,low,close,volume\n';
        for (const row of data)
          csv += `${row[0]},${row[1]},${row[2]},${row[3]},${row[4]},${row[5]||0}\n`;
        writeFileSync(outPath, csv);

        manifest[key] = 'done';
        saveManifest(manifest);
        totalBars += data.length;
        log(`  Saved: ${outPath} | Total bars so far: ${totalBars.toLocaleString()}`);
        await new Promise(r => setTimeout(r, 1000));
        break;

      } catch (err) {
        attempts++;
        const wait = 3000 * Math.pow(2, attempts);
        log(`  ERROR attempt ${attempts}: ${err.message} — retry in ${wait/1000}s`);
        await new Promise(r => setTimeout(r, wait));
      }
    }
  }

  log(`=== Done. Total bars: ${totalBars.toLocaleString()} ===`);
}

main().catch(e => { log(`FATAL: ${e}`); process.exit(1); });
