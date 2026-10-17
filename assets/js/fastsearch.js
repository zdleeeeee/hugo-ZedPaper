import * as params from '@params';

const resList = document.getElementById('searchResults');
const sInput = document.getElementById('searchInput');
const searchBox = document.getElementById('searchbox');

let fuse;
let currentElement = null;
let firstResult = null;
let lastResult = null;

const defaultFuseOptions = {
    includeMatches: true,
    distance: 100,
    // Match the complete query by default; fuzzy matching can be opted into.
    threshold: 0,
    ignoreLocation: true,
    keys: ['title', 'permalink', 'summary', 'content']
};

const buildFuseOptions = () => {
    if (!params.fuseOpts) {
        return defaultFuseOptions;
    }

    return {
        isCaseSensitive: params.fuseOpts.iscasesensitive ?? false,
        includeScore: params.fuseOpts.includescore ?? false,
        // Match positions are required to render contextual previews.
        includeMatches: true,
        minMatchCharLength: params.fuseOpts.minmatchcharlength ?? 1,
        shouldSort: params.fuseOpts.shouldsort ?? true,
        findAllMatches: params.fuseOpts.findallmatches ?? false,
        keys: params.fuseOpts.keys ?? defaultFuseOptions.keys,
        location: params.fuseOpts.location ?? 0,
        threshold: params.fuseOpts.threshold ?? defaultFuseOptions.threshold,
        distance: params.fuseOpts.distance ?? defaultFuseOptions.distance,
        ignoreLocation: params.fuseOpts.ignorelocation ?? defaultFuseOptions.ignoreLocation
    };
};

const debounce = (fn, delay) => {
    let timeout;
    return (...args) => {
        clearTimeout(timeout);
        timeout = window.setTimeout(() => fn(...args), delay);
    };
};

const reset = () => {
    currentElement = null;
    firstResult = null;
    lastResult = null;
    resList.innerHTML = '';
    sInput.value = '';
    sInput.focus();
};

const setActiveResult = (element) => {
    document.querySelectorAll('.focus').forEach((item) => item.classList.remove('focus'));

    if (!element) {
        return;
    }

    element.focus();
    element.parentElement?.classList.add('focus');
    currentElement = element;
};

const getMatchRanges = (text, query, match) => {
    const terms = query.trim().split(/\s+/).filter(Boolean)
        .sort((a, b) => b.length - a.length)
        .map(term => term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
    const exact = terms.length
        ? Array.from(text.matchAll(new RegExp(terms.join('|'), params.fuseOpts?.iscasesensitive ? 'g' : 'gi')),
            hit => [hit.index, hit.index + hit[0].length])
        : [];
    // Prefer whole keywords over the scattered character matches of fuzzy search.
    const ranges = exact.length ? exact : (match?.indices ?? []).map(([start, end]) => [start, end + 1]);
    const merged = [];
    for (const [start, end] of ranges.sort((a, b) => a[0] - b[0])) {
        const previous = merged[merged.length - 1];
        if (previous && start <= previous[1]) {
            previous[1] = Math.max(previous[1], end);
        } else {
            merged.push([start, end]);
        }
    }
    return merged;
};

const getHighlightedParts = (text, ranges, excerpt = false) => {
    const windows = [];
    if (excerpt && ranges.length) {
        for (const [from, to] of ranges) {
            const start = Math.max(0, from - 40);
            const end = Math.min(text.length, to + 40);
            const previous = windows[windows.length - 1];
            if (previous && start <= previous[1] && end - previous[0] <= 180) {
                previous[1] = Math.max(previous[1], end);
            } else if (!previous || to > previous[1]) {
                if (windows.length === 5) break;
                // Avoid repeating context when two bounded excerpts overlap.
                const left = Math.max(start, previous?.[1] ?? 0);
                windows.push([left, Math.min(end, left + 180)]);
            }
        }
    } else {
        windows.push([0, excerpt ? Math.min(text.length, 180) : text.length]);
    }
    const parts = [];
    const add = (value, highlight = false) => {
        if (value) parts.push({ text: value, highlight });
    };
    let previousEnd = 0;
    for (const [start, end] of windows) {
        if (start > previousEnd) add('…');
        let cursor = start;
        for (const [from, to] of ranges) {
            if (to <= start || from >= end) continue;
            const left = Math.max(start, from);
            const right = Math.min(end, to);
            add(text.slice(cursor, left));
            add(text.slice(left, right), true);
            cursor = right;
        }
        add(text.slice(cursor, end));
        previousEnd = end;
    }
    if (previousEnd < text.length) add('…');
    return parts;
};

const appendHighlightedText = (element, parts) => {
    for (const part of parts) {
        if (part.highlight) {
            const mark = document.createElement('mark');
            mark.textContent = part.text;
            element.appendChild(mark);
        } else {
            element.appendChild(document.createTextNode(part.text));
        }
    }
};

const renderResults = (results, query = '') => {
    if (!Array.isArray(results) || results.length === 0) {
        resList.innerHTML = '';
        firstResult = lastResult = currentElement = null;
        return;
    }

    const fragment = document.createDocumentFragment();

    for (const result of results) {
        const li = document.createElement('li');
        const matches = result.matches ?? [];
        const title = document.createElement('div');
        title.className = 'search-result-title';
        appendHighlightedText(title, getHighlightedParts(result.item.title,
            getMatchRanges(result.item.title, query, matches.find(match => match.key === 'title'))));

        const text = document.createElement('div');
        text.className = 'search-result-text';
        text.appendChild(title);
        const contentMatch = matches.find(match => match.key === 'content');
        const summaryMatch = matches.find(match => match.key === 'summary');
        const body = contentMatch ? result.item.content : summaryMatch ? result.item.summary : result.item.content || result.item.summary || '';
        if (body) {
            const preview = document.createElement('p');
            preview.className = 'search-result-preview';
            appendHighlightedText(preview, getHighlightedParts(body,
                getMatchRanges(body, query, contentMatch || summaryMatch), true));
            text.appendChild(preview);
        }
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('width', '24');
        svg.setAttribute('height', '24');
        svg.setAttribute('viewBox', '0 0 24 24');
        svg.setAttribute('fill', 'none');
        svg.setAttribute('stroke', 'currentColor');
        svg.setAttribute('stroke-width', '2');
        svg.setAttribute('stroke-linecap', 'round');
        svg.setAttribute('stroke-linejoin', 'round');
        svg.classList.add('feather', 'feather-chevrons-right');

        svg.innerHTML = '<polyline points="13 17 18 12 13 7"></polyline><polyline points="6 17 11 12 6 7"></polyline>';

        const link = document.createElement('a');
        link.className = 'entry-link';
        link.href = result.item.permalink;
        link.setAttribute('aria-label', result.item.title);

        li.appendChild(text);
        li.appendChild(svg);
        li.appendChild(link);
        fragment.appendChild(li);
    }

    resList.innerHTML = '';
    resList.appendChild(fragment);
    firstResult = resList.firstElementChild;
    lastResult = resList.lastElementChild;
};

const performSearch = () => {
    if (!fuse) {
        return;
    }

    const query = sInput.value.trim();
    if (!query) {
        renderResults([]);
        return;
    }

    const searchOptions = params.fuseOpts?.limit ? { limit: params.fuseOpts.limit } : undefined;
    const results = searchOptions ? fuse.search(query, searchOptions) : fuse.search(query);
    renderResults(results, query);
};

const initSearch = async () => {
    if (!sInput || !resList) {
        return;
    }

    sInput.disabled = false;
    sInput.focus();

    try {
        const response = await fetch('../index.json');
        if (!response.ok) {
            throw new Error(`Search index load failed: ${response.status}`);
        }

        const data = await response.json();
        if (data) {
            fuse = new Fuse(data, buildFuseOptions());
        }
    } catch (error) {
        console.error(error);
    }
};

window.addEventListener('load', initSearch);

sInput?.addEventListener('input', debounce(performSearch, 150));

sInput?.addEventListener('search', () => {
    if (!sInput.value) {
        reset();
    }
});

document.addEventListener('keydown', (event) => {
    const { key } = event;
    const active = document.activeElement;
    const isInSearchBox = searchBox?.contains(active);

    if (key === 'Escape') {
        reset();
        return;
    }

    if (!firstResult || !isInSearchBox) {
        return;
    }

    if (key === 'ArrowDown') {
        event.preventDefault();

        if (active === sInput) {
            setActiveResult(firstResult.querySelector('.entry-link'));
        } else if (active?.parentElement !== lastResult) {
            setActiveResult(active?.parentElement?.nextElementSibling?.querySelector('.entry-link'));
        }
    } else if (key === 'ArrowUp') {
        event.preventDefault();

        if (active?.parentElement === firstResult) {
            setActiveResult(sInput);
        } else if (active !== sInput) {
            setActiveResult(active?.parentElement?.previousElementSibling?.querySelector('.entry-link'));
        }
    } else if (key === 'ArrowRight') {
        if (active?.matches?.('.entry-link')) {
            active.click();
        }
    }
});
