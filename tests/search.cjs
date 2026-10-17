// Run with: node tests/search.cjs
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const Fuse = require('../assets/js/fuse.basic.min.js');

const source = fs.readFileSync(path.join(__dirname, '../assets/js/fastsearch.js'), 'utf8');
const context = vm.createContext({
    params: { fuseOpts: { includematches: false } },
    document: { getElementById: () => null, addEventListener: () => {} },
    window: { addEventListener: () => {} }
});
vm.runInContext(source.replace(/^import .*?;\s*/m, ''), context);
const { buildFuseOptions, getMatchRanges, getHighlightedParts } = vm.runInContext(
    '({ buildFuseOptions, getMatchRanges, getHighlightedParts })', context
);
const plain = value => JSON.parse(JSON.stringify(value));
const highlighted = parts => parts.filter(part => part.highlight).map(part => part.text);

// The default search requires the complete query, not approximate character runs.
const precisionFixture = [
    { title: 'Exact', content: 'A friendly HELLO world.' },
    { title: 'Approximate', content: 'helpful yellow fellow' },
    { title: 'Unrelated', content: 'lo and el elsewhere' }
];
const searchTitles = () => new Fuse(precisionFixture, buildFuseOptions())
    .search('hello').map(result => result.item.title);
assert.deepEqual(searchTitles(), ['Exact']);
const configuredOptions = context.params.fuseOpts;
context.params.fuseOpts = undefined;
assert.deepEqual(searchTitles(), ['Exact']);
context.params.fuseOpts = configuredOptions;

// A match deep in the article must show its context, rather than the introduction.
const content = 'Unrelated introduction. ' + 'Padding. '.repeat(50) + 'Before the needle, after the needle. ' + 'Ending. '.repeat(50);
const result = new Fuse([{ title: 'Example', content }], buildFuseOptions()).search('needle')[0];
assert.ok(result.matches?.some(match => match.key === 'content'));
const ranges = getMatchRanges(content, 'needle', result.matches.find(match => match.key === 'content'));
const parts = plain(getHighlightedParts(content, ranges, true));
assert.ok(parts.map(part => part.text).join('').includes('Before the needle, after the needle.'));
assert.ok(!parts.map(part => part.text).join('').includes('Unrelated introduction.'));
assert.deepEqual(highlighted(parts), ['needle', 'needle']);

// Chinese, case-insensitive keywords, and regex metacharacters remain literal text.
assert.deepEqual(highlighted(plain(getHighlightedParts('这里是正文匹配示例。', getMatchRanges('这里是正文匹配示例。', '正文')))), ['正文']);
assert.deepEqual(highlighted(plain(getHighlightedParts('Hugo and HUGO', getMatchRanges('Hugo and HUGO', 'hugo')))), ['Hugo', 'HUGO']);
assert.deepEqual(plain(getMatchRanges('C++ costs $5.00', 'C++')), [[0, 3]]);
assert.deepEqual(plain(getMatchRanges('C++ costs $5.00', '$5.00')), [[10, 15]]);

// Fuzzy ranges are inclusive in Fuse; overlap must not duplicate text.
const fuzzy = getMatchRanges('colour', 'color', { indices: [[0, 2], [2, 5]] });
assert.deepEqual(plain(getHighlightedParts('colour', fuzzy)), [{ text: 'colour', highlight: true }]);

// Unmatched text is a bounded preview and HTML-looking input remains text.
const fallback = plain(getHighlightedParts('x'.repeat(500), [], true));
assert.ok(fallback.map(part => part.text).join('').length <= 181);
assert.deepEqual(highlighted(fallback), []);
const literal = '<img src=x onerror=alert(1)> & text';
assert.equal(plain(getHighlightedParts(literal, getMatchRanges(literal, 'img'))).map(part => part.text).join(''), literal);

// Distant hits produce up to five previews within the same article result.
const distant = Array.from({ length: 7 }, (_, index) => `Section ${index + 1}: needle. ` + 'padding '.repeat(40)).join('');
const distantParts = plain(getHighlightedParts(distant, getMatchRanges(distant, 'needle'), true));
const distantText = distantParts.map(part => part.text).join('');
assert.deepEqual(highlighted(distantParts), Array(5).fill('needle'));
for (let index = 1; index <= 5; index++) assert.ok(distantText.includes(`Section ${index}: needle.`));
assert.ok(!distantText.includes('Section 6:'));
assert.ok(distantText.includes('…'));

// Nearby matches share their context, without repeated text or extra ellipses.
const nearby = 'Start needle, another needle, end.';
const nearbyParts = plain(getHighlightedParts(nearby, getMatchRanges(nearby, 'needle'), true));
assert.equal(nearbyParts.map(part => part.text).join(''), nearby);
assert.deepEqual(highlighted(nearbyParts), ['needle', 'needle']);

// Dense matches cannot cause the preview to grow to the entire article.
const dense = 'needle '.repeat(1000);
const denseParts = plain(getHighlightedParts(dense, getMatchRanges(dense, 'needle'), true));
assert.ok(denseParts.map(part => part.text).join('').length <= 906);
assert.ok(highlighted(denseParts).length > 1);

// The five-preview limit does not truncate titles.
assert.equal(plain(getHighlightedParts(distant, getMatchRanges(distant, 'needle'))).map(part => part.text).join(''), distant);
console.log('Search tests passed: precision, five contextual previews, merged nearby hits, bounded dense matches, highlights, and fallback.');
