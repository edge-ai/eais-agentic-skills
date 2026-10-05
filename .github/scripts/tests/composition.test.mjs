import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import test from 'node:test';
import vm from 'node:vm';

const require = createRequire(import.meta.url);
const helper = require('node-red-node-test-helper');
helper.init(require.resolve('node-red'));
const core = [
    'common/20-inject', 'common/21-debug', 'common/25-catch',
    'function/15-change', 'function/10-switch', 'sequence/17-split', 'parsers/70-JSON',
].map(path => require(`@node-red/nodes/core/${path}.js`));
const flow = JSON.parse(readFileSync(process.env.EAIS_COMPOSITION_FLOW ?? new URL(
    '../../../skills/node-red-flow-architect/resources/people-count-flow.json', import.meta.url,
)));
const dashboardSource = readFileSync(process.env.EAIS_COMPOSITION_DASHBOARD ?? new URL(
    '../../../skills/node-red-dashboard-architect/resources/people-count-dashboard.js',
    import.meta.url,
), 'utf8').replace(/^import .+;$/gm, '');

function dashboard() {
    let options;
    let receive;
    const warnings = [];
    vm.runInNewContext(dashboardSource, {
        createApp(config) {
            options = config;
            return { mount(id) { assert.equal(id, '#app'); } };
        },
        uibuilder: { onChange(topic, handler) { assert.equal(topic, 'msg'); receive = handler; } },
        console: { warn(text) { warnings.push(text); } },
    }, { timeout: 1000 });
    const state = options.data();
    for (const [name, fn] of Object.entries(options.methods)) state[name] = fn.bind(state);
    options.mounted.call(state);
    return { state, receive, warnings };
}

// Only platform subscription, alarm persistence and UI transport are stubbed.
function platformStubs(RED) {
    function plain(config) { RED.nodes.createNode(this, config); }
    function alarm(config) {
        RED.nodes.createNode(this, config);
        this.evaluations = [];
        this.on('input', (msg, send, done) => {
            try {
                assert.equal(msg.payload.command, 'evaluate');
                assert.equal(config.alarmType, 'numeric');
                assert.equal(config.comparisonOperator, '>');
                assert.ok(Number.isInteger(msg.payload.value) && msg.payload.value >= 0);
                this.evaluations.push(msg.payload.value);
                const triggered = msg.payload.value > Number(config.numericThreshold);
                msg.payload = { alarm: {
                    state: triggered ? 'in_fault' : 'normal', triggered,
                    currentValue: msg.payload.value,
                } };
                send(msg);
                done();
            } catch (error) { done(error); }
        });
    }
    RED.nodes.registerType('callback', plain);
    RED.nodes.registerType('eais-server', plain);
    RED.nodes.registerType('uibuilder', plain);
    RED.nodes.registerType('alarm', alarm);
}

function reaches(from, target, visited = new Set()) {
    if (from === target) return true;
    if (visited.has(from)) return false;
    visited.add(from);
    return (flow.find(node => node.id === from)?.wires ?? []).flat()
        .some(id => reaches(id, target, visited));
}

test('exported graph has real alarm/dashboard paths and no inputless destinations', () => {
    const ids = new Set(flow.map(node => node.id));
    for (const node of flow) {
        for (const target of (node.wires ?? []).flat()) {
            assert.ok(ids.has(target));
            assert.ok(!['inject', 'catch', 'status', 'complete', 'callback'].includes(
                flow.find(candidate => candidate.id === target).type,
            ), `Inputless target ${target}`);
        }
    }
    for (const target of ['people-alarm-0', 'people-alarm-1', 'people-ui']) {
        assert.ok(reaches('people-callback', target), `Disconnected ${target}`);
    }
    assert.ok(reaches('people-catch', 'people-ui'));
    for (const id of ['people-valid', 'people-zero', 'people-missing', 'people-malformed']) {
        const fixture = flow.find(node => node.id === id);
        assert.equal(fixture.once, false);
        assert.equal(fixture.repeat, '');
        assert.equal(fixture.crontab, '');
        assert.ok(reaches(id, 'people-ui'));
    }
});

test('actual Node-RED wiring sends tagged counts, isolated alarms, and explicit unknowns', {
    timeout: 15000,
}, async () => {
    await helper.startServer();
    try {
        await helper.load([...core, platformStubs], flow);
        const ui = helper.getNode('people-ui');
        const view = dashboard();
        const received = [];
        ui.on('input', msg => { received.push(msg); view.receive(msg); });

        async function deliver(send, expected) {
            const start = received.length;
            await new Promise((resolve, reject) => {
                const timer = setTimeout(() => {
                    ui.off('input', check);
                    reject(new Error(`Expected ${expected} messages; got ${received.length - start}`));
                }, 1500);
                function check() {
                    if (received.length - start >= expected) {
                        clearTimeout(timer);
                        ui.off('input', check);
                        resolve();
                    }
                }
                ui.on('input', check);
                send();
            });
            return received.slice(start);
        }
        const inject = id => helper.getNode(id).receive({});
        const callback = payload => helper.getNode('people-callback').send({ payload });
        const alarm0 = helper.getNode('people-alarm-0');
        const alarm1 = helper.getNode('people-alarm-1');

        if (process.env.EAIS_COMPOSITION_CALLBACK_FIXTURES) {
            const fixtures = JSON.parse(readFileSync(process.env.EAIS_COMPOSITION_CALLBACK_FIXTURES));
            for (const fixture of fixtures) {
                const expected = fixture.outcome === 'counts' ? 3 : 1;
                const messages = await deliver(() => callback(fixture.payload), expected);
                assert.equal(messages[0].topic, fixture.outcome);
                if (fixture.semantic_expected === 'unknown' && fixture.outcome === 'counts') {
                    // Observe a generated callback's false-zero regression without
                    // silently treating its semantic quality as a passing fixture.
                    assert.equal(view.state.bySource[0].count, 0);
                    assert.equal(view.state.bySource[1].count, 0);
                    assert.equal(view.state.bySource[0].alarm, 'normal');
                    assert.equal(view.state.bySource[1].alarm, 'normal');
                }
            }
            // Keep the fixed Inject checks independent of optional generated probes.
            alarm0.evaluations.length = 0;
            alarm1.evaluations.length = 0;
        }

        let messages = await deliver(() => inject('people-valid'), 3);
        assert.equal(messages[0].topic, 'counts');
        assert.deepEqual(messages[0].payload, [
            { source_id: 0, count: 3 }, { source_id: 1, count: 1 },
        ]);
        assert.deepEqual(messages.filter(msg => msg.topic === 'alarm')
            .map(msg => [msg.source_id, msg.payload.alarm.state]).sort(),
        [[0, 'in_fault'], [1, 'normal']]);
        assert.equal(view.state.bySource[0].alarm, 'in_fault');
        assert.equal(view.state.bySource[1].alarm, 'normal');

        await deliver(() => inject('people-zero'), 3);
        assert.equal(view.state.formatCount(view.state.bySource[0].count), 0);
        assert.equal(view.state.bySource[0].alarm, 'normal');
        assert.deepEqual(alarm0.evaluations, [3, 0]);
        assert.deepEqual(alarm1.evaluations, [1, 0]);

        const map = (a, b) => Object.fromEntries([a, b].map((count, id) => [id, {
            source_id: id, obj_counter: { person: { max_val: count } },
        }]));
        await deliver(() => callback([{ data: map(99, 99) }, { data: map(2, 4) }]), 3);
        assert.equal(view.state.bySource[0].alarm, 'normal');
        assert.equal(view.state.bySource[1].alarm, 'in_fault');

        for (const id of ['people-missing', 'people-malformed']) {
            messages = await deliver(() => inject(id), 1);
            assert.equal(messages[0].topic, 'unknown');
            assert.equal(view.state.bySource[0].count, null);
            assert.equal(view.state.bySource[1].alarm, 'unknown');
            assert.ok(view.state.error);
        }
        for (const payload of [{}, null, [], { 0: map(1, 1)[0] }, map(-1, 1),
            map('3', 1), map(0.5, 1), map(null, 1),
            { ...map(0, 1), extra: {} }]) {
            messages = await deliver(() => callback(payload), 1);
            assert.equal(messages[0].topic, 'unknown');
        }
        assert.deepEqual(alarm0.evaluations, [3, 0, 2]);
        assert.deepEqual(alarm1.evaluations, [1, 0, 4]);

        messages = await deliver(() => alarm0.error(
            new Error('Synthetic alarm evaluation failure'), { source_id: 0 },
        ), 1);
        assert.equal(messages[0].topic, 'unknown');
        assert.equal(view.state.bySource[0].alarm, 'unknown');
        assert.equal(view.state.bySource[1].count, null);
        assert.match(view.state.error, /Synthetic alarm evaluation failure/);

        await deliver(() => callback(JSON.stringify(map(1, 2))), 3);
        assert.equal(view.state.bySource[0].count, 1);
        assert.equal(view.state.bySource[1].count, 2);
        view.receive({ topic: 'alarm', source_id: 0, payload: { alarm: { state: 'unknown' } } });
        assert.equal(view.state.bySource[0].alarm, 'unknown');
        assert.equal(view.state.bySource[0].count, null);
        assert.ok(view.warnings.length);
        for (let i = 0; i < 101; i++) view.receive({ topic: 'unknown', payload: {} });
        assert.equal(view.state.messages.length, 100);
        view.state.clearMessages();
        assert.equal(view.state.messages.length, 0);
    } finally {
        await helper.unload();
        await helper.stopServer();
    }
});

test('dashboard rejects stale alarm values, invalid snapshots and unexpected envelopes', () => {
    const { state, receive, warnings } = dashboard();
    const counts = { topic: 'counts', payload: [{ source_id: 0, count: 0 }, { source_id: 1, count: 3 }] };
    receive(counts);
    receive({ topic: 'alarm', source_id: 0, payload: {
        alarm: { state: 'normal', triggered: false, currentValue: 99 },
    } });
    assert.equal(state.bySource[0].alarm, 'unknown');
    for (const msg of [null, [], { topic: 'counts', payload: [counts.payload[0]] },
        { topic: 'alarm', source_id: 9 }, { topic: 'unrecognized' }]) {
        receive(msg);
        assert.equal(state.bySource[0].count, null);
        assert.ok(state.error);
    }
    assert.equal(warnings.length, 6);
});
