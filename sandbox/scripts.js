// CX MIRROR — Sandbox Interactivity
document.addEventListener('DOMContentLoaded', () => {
  const qtyMinus = document.querySelector('.qty-btn.minus');
  const qtyPlus = document.querySelector('.qty-btn.plus');
  const qtyVal = document.querySelector('.qty-value');

  if (qtyMinus && qtyPlus && qtyVal) {
    let count = 1;
    qtyPlus.addEventListener('click', () => {
      count = Math.min(10, count + 1);
      qtyVal.textContent = count;
    });
    qtyMinus.addEventListener('click', () => {
      count = Math.max(1, count - 1);
      qtyVal.textContent = count;
    });
  }

  // Ensure fonts are marked loaded
  if (document.fonts) {
    document.fonts.ready.then(() => {
      document.body.setAttribute('data-fonts-loaded', 'true');
    });
  }
});

