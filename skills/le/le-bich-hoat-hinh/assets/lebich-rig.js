// Lê Bích bụng phệ dựng từ bộ rời GỐC (PSD Le_Bich.psd trên Drive art.urah.vn): đầu, thân, tay, chân, râu, mắt, miệng.
// Tóc thường không có trong PSD nên tách từ LE BICH CHARACTERS.jpg (cùng nét gốc). Không vẽ lại nét nào.
// Mỗi bộ phận là một <img> đặt đúng toạ độ gốc trong khung 462×1348; tay và đầu xoay quanh khớp bằng CSS/GSAP.
(function () {
  const RIG = window.LB_RIG; const BB = RIG ? RIG.bbox : window.LB_BBOX;
  const ROOT = (document.currentScript && document.currentScript.src.replace(/[^/]*$/, '')) || '';
  const EYES = { cham: 'Eye__e', hoang: 'Eye__Layer_10', tron: 'Eye__Layer_11', ngan: 'Eye__Layer_12', cuoi: 'Eye__Layer_13', buon: 'Eye__Layer_15' };
  const MOUTHS = { cuoi: 'Mouth__m', ngai: 'Mouth__', chu: 'Mouth__3', thang: 'Mouth__Layer_9', ha: 'Mouth__Layer_14', le: 'Mouth__Layer_16' };
  // Khớp xoay (toạ độ gốc PSD)
  const PIVOT = { armL: [205, 984], armR: [322, 982], head: [248, 1095] };

  const img = (k, cls = '') => {
    const [x0, y0, x1, y1] = BB[k];
    return `<img class="${cls}" src="${RIG ? "data:image/png;base64," + RIG.png_base64[k] : ROOT + "rig/" + k + ".png"}" style="position:absolute;left:${x0}px;top:${y0}px;width:${x1 - x0}px;height:${y1 - y0}px">`;
  };
  const grp = (cls, pivot, rot, inner) =>
    `<div class="${cls}" style="position:absolute;left:0;top:0;width:462px;height:1348px;transform-origin:${pivot[0]}px ${pivot[1]}px;transform:rotate(${rot || 0}deg)">${inner}</div>`;

  /** makeLeBich({eyes, mouth, armL, armR, head, suit, w}) → HTML. w = chiều rộng hiển thị (px); khung cắt 400×620. */
  function makeLeBich(o = {}) {
    const w = o.w || 300, s = w / 400;
    const eyes = Object.values(EYES).map(k => img(k, 'lb-eye lb-e-' + k + (k === EYES[o.eyes || 'cham'] ? '' : ' an'))).join('');
    const mouths = Object.values(MOUTHS).map(k => img(k, 'lb-mouth lb-m-' + k + (k === MOUTHS[o.mouth || 'cuoi'] ? '' : ' an'))).join('');
    const head = grp('lb-head', PIVOT.head, o.head, img('Le_Bich__head') + img('Hair_tach_tu_CHARACTERS') + img('Rau__Rau_basic') + eyes + mouths);
    const body = o.suit ? img('Le_Bich_cong_so__Body') : img('Le_Bich__body');
    return `<div class="lb" style="position:relative;width:${w}px;height:${620 * s}px">
      <div class="lb-all" style="position:absolute;left:0;top:0;width:462px;height:1348px;transform-origin:0 0;transform:scale(${s}) translate(-40px,-690px)">
        <div class="lb-legs">${img('Le_Bich__leg_R')}${img('Le_Bich__leg_L')}</div>
        ${grp('lb-armL', PIVOT.armL, o.armL, img('Le_Bich__hand_L'))}
        <div class="lb-body" style="position:absolute;left:0;top:0;width:462px;height:1348px;transform-origin:246px 1240px">${body}</div>
        ${grp('lb-armR', PIVOT.armR, o.armR, img('Le_Bich__hand_R'))}
        ${head}
      </div></div>`;
  }
  const CSS = `.lb img{user-select:none;pointer-events:none}.lb .an{display:none}`;
  window.LB = { makeLeBich, CSS, EYES, MOUTHS };
})();
