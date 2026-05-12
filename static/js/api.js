/**
 * Utilitários para comunicação com a API do backend TechShop.
 * 
 * Este módulo fornece funções para:
 * - Gerenciar o carrinho de compras
 * - Aplicar e remover cupons
 * - Buscar produtos
 * - Exibir mensagens de erro/sucesso
 */

const API_BASE_URL = '/api';
const CART_BASE_URL = '/cart';

/**
 * Classe para gerenciar mensagens de feedback ao usuário.
 */
class NotificationManager {
  /**
   * Exibe uma notificação de sucesso.
   * @param {string} message - Mensagem a exibir
   * @param {number} duration - Duração em ms (padrão 3000)
   */
  static success(message, duration = 3000) {
    this.show(message, 'success', duration);
  }

  /**
   * Exibe uma notificação de erro.
   * @param {string} message - Mensagem a exibir
   * @param {number} duration - Duração em ms (padrão 4000)
   */
  static error(message, duration = 4000) {
    this.show(message, 'error', duration);
  }

  /**
   * Exibe uma notificação genérica.
   * @private
   */
  static show(message, type, duration) {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 px-4 py-3 rounded-lg text-white z-50 ${
      type === 'success' ? 'bg-green-500' : 'bg-red-500'
    }`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), duration);
  }
}

/**
 * Gerenciador de carrinho.
 * 
 * Responsável por: adicionar, remover, atualizar e obter estado do carrinho.
 */
class CartManager {
  /**
   * Adiciona um produto ao carrinho.
   * @param {number} productId - ID do produto
   * @param {number} quantity - Quantidade (padrão 1)
   * @returns {Promise<Object>} Resumo atualizado do carrinho
   */
  static async addItem(productId, quantity = 1) {
    try {
      const response = await fetch(`${CART_BASE_URL}/add`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_id: productId, quantity })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Erro ao adicionar ao carrinho');
      }

      const summary = await response.json();
      NotificationManager.success('Produto adicionado ao carrinho!');
      this.updateCartBadge();
      return summary;
    } catch (error) {
      NotificationManager.error(error.message);
      console.error('Erro ao adicionar item:', error);
    }
  }

  /**
   * Remove um produto do carrinho.
   * @param {number} productId - ID do produto
   * @returns {Promise<Object>} Resumo atualizado do carrinho
   */
  static async removeItem(productId) {
    try {
      const response = await fetch(`${CART_BASE_URL}/remove/${productId}`, {
        method: 'DELETE'
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Erro ao remover do carrinho');
      }

      const summary = await response.json();
      NotificationManager.success('Produto removido do carrinho!');
      this.updateCartBadge();
      return summary;
    } catch (error) {
      NotificationManager.error(error.message);
      console.error('Erro ao remover item:', error);
    }
  }

  /**
   * Obtém o resumo atual do carrinho.
   * @returns {Promise<Object>} CartSummary com subtotal, descontos e total
   */
  static async getSummary() {
    try {
      const response = await fetch(`${CART_BASE_URL}/summary`);
      
      if (!response.ok) {
        throw new Error('Erro ao obter resumo do carrinho');
      }

      return await response.json();
    } catch (error) {
      console.error('Erro ao obter resumo:', error);
      return null;
    }
  }

  /**
   * Aplica um cupom ao carrinho.
   * @param {string} couponCode - Código do cupom (ex: "SAVE10")
   * @returns {Promise<Object>} CartSummary atualizado com desconto aplicado
   */
  static async applyCoupon(couponCode) {
    try {
      const response = await fetch(`${CART_BASE_URL}/apply-coupon`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: couponCode.toUpperCase() })
      });

      if (!response.ok) {
        const error = await response.json();
        const message = error.detail === 'Coupon not found' 
          ? 'Cupom não encontrado'
          : error.detail || 'Erro ao aplicar cupom';
        throw new Error(message);
      }

      const summary = await response.json();
      NotificationManager.success('Cupom aplicado com sucesso!');
      return summary;
    } catch (error) {
      NotificationManager.error(error.message);
      console.error('Erro ao aplicar cupom:', error);
    }
  }

  /**
   * Remove o cupom aplicado ao carrinho.
   * @returns {Promise<Object>} CartSummary sem desconto de cupom
   */
  static async removeCoupon() {
    try {
      const response = await fetch(`${CART_BASE_URL}/coupon`, {
        method: 'DELETE'
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Erro ao remover cupom');
      }

      const summary = await response.json();
      NotificationManager.success('Cupom removido');
      return summary;
    } catch (error) {
      NotificationManager.error(error.message);
      console.error('Erro ao remover cupom:', error);
    }
  }

  /**
   * Atualiza o badge do carrinho na interface.
   * @private
   */
  static updateCartBadge() {
    const badge = document.querySelector('[data-cart-count]');
    if (badge) {
      // Aqui você poderia buscar o novo count via API
      // Por enquanto, é atualizado server-side
      location.reload();
    }
  }
}

/**
 * Gerenciador de busca de produtos.
 */
class SearchManager {
  /**
   * Busca produtos pelo termo de busca.
   * @param {string} query - Termo de busca
   * @param {string} category - Categoria (opcional)
   * @returns {Promise<Array>} Lista de produtos encontrados
   */
  static async search(query, category = null) {
    try {
      let url = `${API_BASE_URL}/search?q=${encodeURIComponent(query)}`;
      if (category) {
        url += `&category=${encodeURIComponent(category)}`;
      }

      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error('Erro ao buscar produtos');
      }

      return await response.json();
    } catch (error) {
      console.error('Erro na busca:', error);
      return [];
    }
  }

  /**
   * Valida o termo de busca.
   * @param {string} query - Termo a validar
   * @returns {boolean} Válido se tem pelo menos 2 caracteres
   */
  static isValidQuery(query) {
    return query && query.trim().length >= 2;
  }
}

/**
 * Gerenciador de formatação de dados.
 */
class FormatManager {
  /**
   * Formata um valor para moeda brasileira.
   * @param {number} value - Valor a formatar
   * @returns {string} Valor formatado (ex: "R$ 1.234,56")
   */
  static formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  }

  /**
   * Formata um percentual.
   * @param {number} value - Valor do percentual
   * @returns {string} Percentual formatado (ex: "25,5%")
   */
  static formatPercent(value) {
    return new Intl.NumberFormat('pt-BR', {
      style: 'percent',
      minimumFractionDigits: 1
    }).format(value / 100);
  }

  /**
   * Trunca um texto com elipsis.
   * @param {string} text - Texto a truncar
   * @param {number} length - Comprimento máximo
   * @returns {string} Texto truncado
   */
  static truncate(text, length = 50) {
    return text.length > length ? text.substring(0, length) + '...' : text;
  }
}

// Exportar para uso global
window.CartManager = CartManager;
window.SearchManager = SearchManager;
window.FormatManager = FormatManager;
window.NotificationManager = NotificationManager;
