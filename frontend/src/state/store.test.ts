import { describe, expect, test } from 'vitest';
import { useStore } from './store';

describe('store', () => {
  test('has default node count', () => {
    expect(useStore.getState().nodes).toHaveLength(3);
  });
});
