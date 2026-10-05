import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import jsonata from 'jsonata';

const guide = readFileSync(new URL(
    '../../../skills/node-red-flow-architect/resources/jsonata-cheatsheet.md',
    import.meta.url,
), 'utf8');
const section = guide.split('## Tested callback adapter: keyed class counts')[1];
assert.ok(section, 'Expected the documented keyed-count adapter');
const expression = section.match(/```jsonata\n([\s\S]*?)```/)[1];
const adapter = jsonata(expression);
const source = (id, count) => ({
    source_id: id, obj_counter: { person: { max_val: count } },
});
const evaluate = payload => adapter.evaluate({ payload });

test('detection-list example distinguishes an empty list from unavailable telemetry', async () => {
    const example = guide.split('## Example: People counting without a Function node')[1]
        .match(/```jsonata\n([\s\S]*?)```/)[1];
    const countPeople = jsonata(example);
    assert.deepEqual(await countPeople.evaluate({ payload: { objects: [] } }),
        { command: 'evaluate', value: 0 });
    assert.deepEqual(await countPeople.evaluate({ payload: { objects: [
        { label: 'person' }, { label: 'car' },
    ] } }), { command: 'evaluate', value: 1 });
    await assert.rejects(countPeople.evaluate({ payload: {} }));
});

test('normalizes empty, singleton and multiple source maps to arrays', async () => {
    assert.deepEqual(await evaluate({}), []);
    assert.deepEqual(await evaluate({ demo: source('demo', 3) }), [
        { source_id: 'demo', count: 3 },
    ]);
    assert.deepEqual(await evaluate({ '0': source(0, 0), '1': source(1, 3) }), [
        { source_id: 0, count: 0 }, { source_id: 1, count: 3 },
    ]);
});

test('uses only the latest time window, including an empty latest result', async () => {
    assert.deepEqual(await evaluate([
        { since: 0, until: 1, data: { demo: source('demo', 99) } },
        { since: 1, until: 2, data: { demo: source('demo', 0) } },
    ]), [{ source_id: 'demo', count: 0 }]);
    assert.deepEqual(await evaluate([]), []);
    assert.deepEqual(await evaluate([{ data: {} }]), []);
});

test('requires JSON-node parsing for serialized input and rejects malformed data', async () => {
    const encoded = JSON.stringify({ demo: source('demo', 3) });
    await assert.rejects(evaluate(encoded), { message: 'Parse callback JSON with a JSON node first' });
    assert.deepEqual(await evaluate(JSON.parse(encoded)), [{ source_id: 'demo', count: 3 }]);
    for (const payload of [
        null, 4, true, [{ data: null }], { demo: null }, { demo: {} },
        { demo: source('demo', '3') }, { demo: source('demo', -1) },
        { demo: source('demo', 0.5) }, { demo: source(false, 3) },
    ]) {
        await assert.rejects(evaluate(payload));
    }
});

test('the documented Inject payload reaches the adapter without a nested envelope', async () => {
    const inject = JSON.parse(section.match(/```json\n([\s\S]*?)```/)[1]);
    assert.equal(inject.payloadType, 'json');
    const payload = JSON.parse(inject.payload);
    assert.deepEqual(await evaluate(payload), [{ source_id: 'demo', count: 3 }]);
    await assert.rejects(evaluate({ payload }));
    assert.equal(inject.once, false);
    assert.equal(inject.repeat, '');
    assert.equal(inject.crontab, '');
});
