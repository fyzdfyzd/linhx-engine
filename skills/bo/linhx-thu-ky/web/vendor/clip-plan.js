/*
 * Video-matrix clip planner (pure, UMD for tests). Two naming schemes:
 *  - legacy: every pair exists as `${from}_${to}.mp4` (loops are `${s}_${s}.mp4`);
 *  - clip map: `clips["from>to"] = [file, …]` with variants. States are pose nodes (the pose the clip ends on).
 *    A target may name a GROUP: "talk" = "talk" plus every "talk-…" state, so talk-01 → talk-02 → talk-01 keeps
 *    talking without a talk>talk loop. Routes use the shortest chain of clips; a group with no clip inside it is a
 *    one-shot gesture (wave, heart) that returns to idle; a dead end (no clip out) cuts to the target's loop.
 */
(function (factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (typeof window !== 'undefined') window.ClipPlan = api;
})(function () {
  'use strict';

  function pick(list, rnd) { return list.at(Math.floor((rnd || Math.random)() * list.length) % list.length); }
  function inGroup(s, g) { return s === g || (typeof s === 'string' && s.startsWith(`${g}-`)); }

  function edges(clips) {
    return Object.keys(clips).map(k => { const [from, to] = k.split('>'); return { from, to, files: clips[k] }; })
      .filter(e => Array.isArray(e.files) && e.files.length);
  }

  function clip(clips, from, to, rnd) {
    if (!clips) return `${from}_${to}.mp4`;
    const list = clips[`${from}>${to}`];
    return Array.isArray(list) && list.length ? pick(list, rnd) : null;
  }

  /** Does the group have a clip that stays inside it (i.e. it can loop)? */
  function hasLoop(clips, g) { return !clips || edges(clips).some(e => inGroup(e.from, g) && inGroup(e.to, g)); }

  /** First clips of every shortest route (≥1 clip) from `from` into group `g`. */
  function firstSteps(all, from, g) {
    const seen = new Map([[from, null]]);
    let frontier = [from];
    while (frontier.length) {
      const hits = [];
      const next = [];
      for (const s of frontier) {
        for (const e of all.filter(x => x.from === s)) {
          const first = seen.get(s) || e;
          if (inGroup(e.to, g)) hits.push(first);
          if (!seen.has(e.to)) { seen.set(e.to, first); next.push(e.to); }
        }
      }
      if (hits.length) return hits;
      frontier = next;
    }
    return [];
  }

  /** A clip inside the group to cut to when no route exists (prefers a true loop s>s). */
  function loop(clips, g, rnd) {
    const inside = edges(clips).filter(e => inGroup(e.from, g) && inGroup(e.to, g));
    const e = inside.find(x => x.from === x.to) || inside[0];
    return e ? { file: pick(e.files, rnd), state: e.to } : null;
  }

  function step(clips, from, g, rnd) {
    const all = edges(clips);
    const hits = firstSteps(all, from, g);
    if (hits.length) { const e = pick(hits, rnd); return { file: pick(e.files, rnd), state: e.to }; }
    return loop(clips, g, rnd);
  }

  /**
   * What to play when the current clip ends. Returns {file, state, next, oneShot}:
   * file = clip to play (null = keep going), state = state after it, next = the target to aim for afterwards.
   */
  function plan(clips, from, target, idle, rnd) {
    if (!clips) return legacy(from, target, idle);
    // A gesture state with no clip out ends on the idle frame (one-shots return to idle): plan from idle.
    if (idle && from !== idle && !edges(clips).some(e => e.from === from)) from = idle;
    const loops = hasLoop(clips, target);
    if (!loops && inGroup(from, target)) return { ...(step(clips, from, idle, rnd) || { file: null, state: from }), next: idle, oneShot: false };
    const s = step(clips, from, target, rnd) || step(clips, from, idle, rnd) || { file: null, state: from };
    const oneShot = !loops && inGroup(s.state, target);
    return { file: s.file, state: s.state, next: oneShot ? idle : target, oneShot };
  }

  function legacy(from, target) { return { file: `${from}_${target}.mp4`, state: target, next: target, oneShot: false }; }

  /** Summary for the Studio/onboarding asset checklist: loop groups, one-shot groups and dead-end states. */
  function coverage(vm) {
    const states = (vm && vm.states) || [];
    const clips = vm && vm.clips;
    if (!clips) return { states: states.length, loops: states.length, oneShots: [], deadEnds: [] };
    const all = edges(clips);
    const groups = [...new Set(states.map(s => s.replace(/-\d+$/, '')))];
    return {
      states: states.length,
      loops: groups.filter(g => hasLoop(clips, g)).length,
      oneShots: groups.filter(g => !hasLoop(clips, g)),
      deadEnds: states.filter(s => all.some(e => e.to === s) && !all.some(e => e.from === s) && hasLoop(clips, s.replace(/-\d+$/, ''))),
    };
  }

  return { plan, clip, hasLoop, loop, coverage, inGroup };
});
