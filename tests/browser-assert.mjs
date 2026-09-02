const d = process.env.WD_DOM || '';
const checks = [
  ['expected locale html', /<html\b[^>]*\blang="(?:vi|en)"/.test(d)],
  ['mobile menu control', d.includes('data-menu-toggle')],
  ['all local images have geometry', !/<img\b[^>]*\bsrc="\/(?!\/)[^"]*"[^>]*\b(?:width|height)="(?:0|)"/.test(d)],
  ['partners clean asset contract', !d.includes('b2b-vorigin-premium.webp')],
];
for (const [name, ok] of checks) { if (!ok) { console.error(`FAIL ${name}`); process.exit(1); } console.log(`PASS ${name}`); }
