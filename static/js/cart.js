/**
 * Inicialização de event listeners para o carrinho.
 * 
 * Executa quando o DOM está pronto e configura:
 * - Formulário de aplicação de cupom
 * - Botões de remover do carrinho
 * - Atualização do resumo
 */

document.addEventListener('DOMContentLoaded', function() {
  initCartForm();
  initRemoveButtons();
  initSearchForm();
});

/**
 * Inicializa o formulário de aplicação de cupom.
 */
function initCartForm() {
  const couponForm = document.getElementById('couponForm');
  
  if (!couponForm) return;

  couponForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const couponInput = couponForm.querySelector('input[name="coupon_code"]');
    const code = couponInput.value.trim();

    if (!code) {
      NotificationManager.error('Digite um código de cupom');
      return;
    }

    const summary = await CartManager.applyCoupon(code);
    if (summary) {
      couponInput.value = '';
      updateCartSummary(summary);
    }
  });
}

/**
 * Inicializa botões de remover item do carrinho.
 */
function initRemoveButtons() {
  const removeButtons = document.querySelectorAll('[data-remove-product]');
  
  removeButtons.forEach(button => {
    button.addEventListener('click', async (e) => {
      e.preventDefault();
      
      const productId = parseInt(button.dataset.removeProduct);
      
      if (confirm('Tem certeza que deseja remover este item?')) {
        const summary = await CartManager.removeItem(productId);
        if (summary) {
          // Remover item da tela
          const itemElement = button.closest('[data-cart-item]');
          if (itemElement) {
            itemElement.remove();
            updateCartSummary(summary);
            
            // Se carrinho vazio, recarregar página
            const items = document.querySelectorAll('[data-cart-item]');
            if (items.length === 0) {
              setTimeout(() => location.reload(), 1000);
            }
          }
        }
      }
    });
  });
}

/**
 * Inicializa o formulário de busca.
 */
function initSearchForm() {
  const searchForm = document.querySelector('[data-search-form]');
  const searchInput = document.querySelector('[data-search-input]');
  
  if (!searchForm || !searchInput) return;

  searchForm.addEventListener('submit', (e) => {
    e.preventDefault();
    
    const query = searchInput.value.trim();
    
    if (!SearchManager.isValidQuery(query)) {
      NotificationManager.error('Digite pelo menos 2 caracteres para buscar');
      return;
    }

    // Redirecionar para página de busca
    window.location.href = `/search?q=${encodeURIComponent(query)}`;
  });
}

/**
 * Atualiza o resumo do carrinho na interface.
 * @param {Object} summary - CartSummary do backend
 */
function updateCartSummary(summary) {
  if (!summary) return;

  // Atualizar subtotal
  const subtotalEl = document.getElementById('cartSubtotal');
  if (subtotalEl) {
    subtotalEl.textContent = FormatManager.formatCurrency(summary.subtotal);
  }

  // Atualizar desconto de cupom
  const couponDiscountEl = document.getElementById('cartCouponDiscount');
  if (couponDiscountEl) {
    if (summary.coupon_discount > 0) {
      couponDiscountEl.closest('[data-coupon-row]').style.display = 'flex';
      couponDiscountEl.textContent = `-${FormatManager.formatCurrency(summary.coupon_discount)}`;
    } else {
      couponDiscountEl.closest('[data-coupon-row]').style.display = 'none';
    }
  }

  // Atualizar desconto progressivo
  const progressiveDiscountEl = document.getElementById('cartProgressiveDiscount');
  if (progressiveDiscountEl) {
    if (summary.progressive_discount > 0) {
      progressiveDiscountEl.closest('[data-progressive-row]').style.display = 'flex';
      progressiveDiscountEl.textContent = `-${FormatManager.formatCurrency(summary.progressive_discount)}`;
    } else {
      progressiveDiscountEl.closest('[data-progressive-row]').style.display = 'none';
    }
  }

  // Atualizar total
  const totalEl = document.getElementById('cartTotal');
  if (totalEl) {
    totalEl.textContent = FormatManager.formatCurrency(summary.total);
  }
}

/**
 * Adiciona um produto ao carrinho (chamado de onclick de botão).
 * @param {number} productId - ID do produto
 * @param {string} productName - Nome do produto (para exibir no toast)
 */
async function addProductToCart(productId, productName) {
  await CartManager.addItem(productId, 1);
}

/**
 * Aplica um cupom (chamado de onclick de botão).
 * @param {string} couponCode - Código do cupom
 */
async function applyCouponAction(couponCode) {
  const summary = await CartManager.applyCoupon(couponCode);
  if (summary) {
    updateCartSummary(summary);
    
    // Remover o botão de cupom e exibir removedor
    const button = event.target;
    button.style.display = 'none';
    button.nextElementSibling?.style.display = 'inline-block';
  }
}

/**
 * Remove um cupom (chamado de onclick de botão).
 */
async function removeCouponAction() {
  const summary = await CartManager.removeCoupon();
  if (summary) {
    updateCartSummary(summary);
    
    // Remover o botão de removedor e exibir cupom novamente
    const button = event.target;
    button.style.display = 'none';
    button.previousElementSibling?.style.display = 'inline-block';
  }
}
