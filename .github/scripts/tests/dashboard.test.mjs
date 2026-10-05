import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import vm from 'node:vm';

const guide = readFileSync(new URL(
    '../../../skills/node-red-dashboard-architect/resources/STARTING_GUIDE.md',
    import.meta.url,
), 'utf8');
const examples = [...guide.matchAll(/^```javascript\s*\n([\s\S]*?)^```\s*$/gm)];
assert.equal(examples.length, 1, 'Expected one complete dashboard JavaScript example');
const source = examples[0][1].replace(/^import .+;[^\n]*$/gm, '');

test('count formatter preserves zero and distinguishes unknown measurements', () => {
    const skill = readFileSync(new URL(
        '../../../skills/node-red-dashboard-architect/SKILL.md', import.meta.url,
    ), 'utf8');
    const formatter = skill.match(/```javascript\n(function formatCount[\s\S]*?)```/)[1];
    const formatCount = vm.runInNewContext(`${formatter}\nformatCount`, {}, { timeout: 1000 });
    assert.equal(formatCount(0), 0);
    assert.equal(formatCount(3), 3);
    for (const value of [null, undefined, '0', {}, NaN, Infinity]) {
        assert.equal(formatCount(value), 'unknown');
    }
});
function dashboard() {
    let options;
    let receive;
    let mounted;
    const warnings = [];
    const events = [];
    vm.runInNewContext(source, {
        createApp(config) {
            options = config;
            return { mount(selector) { mounted = selector; } };
        },
        uibuilder: {
            onChange(name, handler) {
                assert.equal(name, 'msg');
                receive = handler;
            },
            eventSend(event) { events.push(event); },
        },
        console: { warn(message) { warnings.push(message); } },
    }, { timeout: 1000 });
    assert.equal(mounted, '#app');
    const state = options.data();
    options.mounted.call(state);
    return { state, receive, options, warnings, events };
}

test('keeps exactly the newest 100 messages and supports clearing', () => {
    const { state, receive, options } = dashboard();
    for (let i = 0; i < 101; i++) receive({ payload: i });
    assert.equal(state.messages.length, 100);
    assert.equal(state.messages[0].payload, 100);
    assert.equal(state.messages[99].payload, 1);
    options.methods.clearMessages.call(state);
    assert.equal(state.messages.length, 0);
});

test('rejects malformed envelopes with explicit warnings', () => {
    const { state, receive, warnings } = dashboard();
    for (const msg of [null, undefined, 1, 'text', []]) receive(msg);
    assert.equal(state.messages.length, 0);
    assert.equal(warnings.length, 5);
});

test('formats zero counts, ignores nullable sources, and uses the latest batch', () => {
    const { state, receive, options } = dashboard();
    receive({ payload: [
        { data: { old: { obj_counter: { car: 99 } } } },
        { data: { absent: null, current: { obj_counter: { car: 0 } } } },
    ] });
    const formatted = options.computed.formattedMessages.call(state);
    assert.deepEqual(JSON.parse(formatted[0].formattedPayload),
        [{ source: 'current', obj_counter: { car: 0 } }]);
    for (const payload of [[], null, [{ data: null }], [{ data: { source: null } }]]) {
        receive({ payload });
        assert.doesNotThrow(() => options.computed.formattedMessages.call(state));
    }
});

test('forwards UI events to UIBuilder', () => {
    const { state, options, events } = dashboard();
    const event = { type: 'click' };
    options.methods.doEvent.call(state, event);
    assert.equal(events[0], event);
});
