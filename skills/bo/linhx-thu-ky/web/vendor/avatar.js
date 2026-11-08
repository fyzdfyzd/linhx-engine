/*
 * AvatarController — full-screen character background.
 *  - video_matrix: dual-video crossfade; each state change plays a transition clip, then loops the target state.
 *    Clip names come from ClipPlan (legacy `${from}_${to}.mp4`, or an explicit `clips` map with variants and
 *    one-shot gestures). The pose→state map comes from the character config (no hardcoded names).
 *  - image_poses: crossfade between pose images (with numbered variants such as talking_1..3).
 */
(function (root) {
  'use strict';

  const POSE_GROUPS = {
    idle: ['idle'],
    listening: ['listening_1', 'listening_2', 'listening_3', 'listening'],
    talking: ['talking_1', 'talking_2', 'talking_3', 'talking'],
    thinking: ['thinking'],
    greeting: ['greeting'],
    excited: ['laughing', 'talking_2', 'talking'],
    action: ['blessing', 'greeting'],
    laughing: ['laughing'],
    surprised: ['surprised'],
    blessing: ['blessing'],
  };

  class AvatarController {
    constructor(videoA, videoB, imgEl, placeholderEl) {
      this.videoA = videoA; this.videoB = videoB; this.imgEl = imgEl; this.placeholderEl = placeholderEl;
      this.active = videoA;
      this.assetType = null;
      this.currentPose = 'idle';
      this.currentState = null; this.targetState = null;
      this.basePath = ''; this.poses = {}; this.stateMap = {};
      this.onPoseChange = null;
      this.variantIndex = {};
    }

    loadCharacter(config) {
      this.assetType = config.assetType;
      this.currentPose = 'idle';
      if (config.assetType === 'video_matrix' && config.videoMatrix) {
        const vm = config.videoMatrix;
        this.basePath = vm.basePath;
        this.clips = vm.clips || null;
        const d = vm.defaultState || vm.states[0];
        this.stateMap = {
          idle: d,
          talking: vm.talkState || d,
          excited: vm.talkExcitedState || vm.talkState || d,
          greeting: vm.waveState || d,
          action: vm.actionState || vm.waveState || d,
          listening: vm.listeningState || d,
          thinking: vm.thinkingState || d,
          ...(vm.poseMap || {}),
        };
        this.currentState = d; this.targetState = d;
        this.videoA.onended = () => this.#nextClip();
        this.videoB.onended = () => this.#nextClip();
        this.failures = 0;
        this.videoA.onerror = () => this.#recover(this.videoA);
        this.videoB.onerror = () => this.#recover(this.videoB);
        this.videoA.onplaying = () => { this.failures = 0; };
        this.videoB.onplaying = () => { this.failures = 0; };
        if (!this.resumeBound) { // browsers pause media in hidden tabs; resume the active clip when the kiosk is visible again
          this.resumeBound = true;
          document.addEventListener('visibilitychange', () => { const v = this.active; if (!document.hidden && v && v.paused && v.getAttribute('src')) v.play().catch(() => {}); });
        }
        this.imgEl.style.display = 'none';
        const first = root.ClipPlan.clip(this.clips, d, d);
        if (first) this.#play(this.videoA, first, true);
      } else {
        const ip = config.imagePoses || {};
        this.basePath = ip.basePath || '';
        this.poses = {};
        for (const [k, v] of Object.entries(ip)) if (k !== 'basePath' && typeof v === 'string') this.poses[k] = v;
        this.videoA.style.display = 'none'; this.videoB.style.display = 'none';
        this.#showImage('idle');
      }
      if (this.placeholderEl) this.placeholderEl.style.display = 'none';
    }

    setPose(pose) {
      if (!pose || pose === this.currentPose) return;
      const prev = this.currentPose;
      this.currentPose = pose;
      if (this.onPoseChange) this.onPoseChange(prev, pose);
      if (this.assetType === 'video_matrix') {
        const s = this.stateMap[pose] || this.stateMap.idle;
        if (s) this.targetState = s; // applied when the current clip ends (seamless)
      } else this.#showImage(pose);
    }

    /** Aim directly at a video state (stage behaviour: offstage, idle activities). */
    setState(state) {
      if (this.assetType !== 'video_matrix' || !state) return;
      this.currentPose = state;
      this.targetState = state;
    }

    /** Group the character is in or heading to (e.g. "offstage"). */
    get stage() { return { current: this.currentState, target: this.targetState }; }

    #nextClip() {
      const p = root.ClipPlan.plan(this.clips, this.currentState, this.targetState, this.stateMap.idle);
      this.currentState = p.state;
      if (p.oneShot) { this.targetState = p.next; this.currentPose = 'idle'; } // a gesture plays once, then idle
      if (p.file) this.#crossfade(p.file);
    }

    /** A clip failed: try the target loop, then idle; stop after 3 failures in a row (no request storm). */
    #recover(video) {
      if (video !== this.active) return;
      this.failures = (this.failures || 0) + 1;
      if (this.failures >= 3) {
        this.videoA.removeAttribute('src'); this.videoB.removeAttribute('src');
        if (this.placeholderEl) this.placeholderEl.style.display = 'flex';
        return;
      }
      const d = this.failures === 1 ? this.targetState : this.stateMap.idle;
      if (!d) return;
      const l = this.clips ? root.ClipPlan.loop(this.clips, d) : { file: `${d}_${d}.mp4`, state: d };
      if (!l) return;
      this.currentState = l.state; this.targetState = d;
      this.#play(this.active, l.file, true);
    }

    #play(video, file, visible) {
      video.src = this.basePath + file;
      video.style.display = 'block';
      if (visible) { video.style.opacity = '1'; video.style.zIndex = '2'; }
      video.play().catch(() => {});
    }

    #crossfade(file) {
      const outgoing = this.active;
      const incoming = outgoing === this.videoA ? this.videoB : this.videoA;
      this.active = incoming;
      incoming.style.opacity = '0'; incoming.style.zIndex = '2'; outgoing.style.zIndex = '1';
      const fade = () => {
        incoming.style.opacity = '1'; outgoing.style.opacity = '0';
        setTimeout(() => { outgoing.pause(); }, 650);
      };
      incoming.addEventListener('playing', fade, { once: true });
      this.#play(incoming, file, false);
    }

    #showImage(pose) {
      const variants = (POSE_GROUPS[pose] || [pose]).filter(v => this.poses[v]);
      let file;
      if (variants.length) {
        const i = (this.variantIndex[pose] || 0) % variants.length;
        this.variantIndex[pose] = i + 1;
        file = this.poses[variants[i]];
      } else file = this.poses[pose] || this.poses.idle;
      if (!file) return;
      const src = this.basePath + file;
      const pre = new Image();
      pre.onload = () => {
        this.imgEl.src = src;
        this.imgEl.style.display = 'block';
        this.imgEl.style.opacity = '1';
      };
      pre.src = src;
    }
  }

  root.AvatarController = AvatarController;
})(window);
