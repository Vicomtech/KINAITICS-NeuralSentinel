jest.mock('electron');
jest.mock('python-shell');

const { escapeHtml } = require('../main');

describe('escapeHtml()', () => {
  it('replaces special characters with HTML entities', () => {
    expect(escapeHtml('a&b<c>d"e\'f')).toBe('a&amp;b&lt;c&gt;d&quot;e&#39;f');
  });

  it('handles null and undefined inputs', () => {
    expect(escapeHtml(null)).toBe('null');
    expect(escapeHtml(undefined)).toBe('undefined');
  });
});