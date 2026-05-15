# Scripts de Testes Postman - TechShop API

Use estes scripts na aba **Tests** das requests importadas do Swagger/OpenAPI:

```text
http://127.0.0.1:8000/openapi.json
```

Tambem ha uma collection pronta para importar no Postman:

```text
postman/TechShop API Tests.postman_collection.json
postman/TechShop API Tests.postman_environment.json
```

No Postman, importe os dois arquivos, selecione o ambiente **TechShop Local** e execute
a collection **TechShop API Tests**. Antes de executar, mantenha a API rodando em
`http://127.0.0.1:8000`.

Se o Postman Extension nao resolver variaveis de ambiente, reimporte a collection:
ela tambem esta configurada com URLs locais literais para evitar erro como
`getaddrinfo ENOTFOUND {{base_url}}`.

Os scripts validam:

- status code `200` para operacoes bem-sucedidas;
- status code `400` para falhas de regra de negocio nas rotas que podem falhar assim;
- schema JSON da resposta de sucesso;
- schema JSON da resposta de erro `400`.

Observacoes:

- A API tambem pode retornar `404` em casos como produto ou cupom inexistente. Esses cenarios nao estao aceitos nos scripts abaixo porque o escopo solicitado foi `200/400`.
- Payloads malformados ou campos ausentes podem retornar `422` pela validacao automatica do FastAPI. Para testar `400`, use payloads validos no formato, mas invalidos na regra de negocio, como `quantity: 0` ou cupom sem subtotal minimo.

## GET /api/status

```javascript
const statusSchema = {
  type: "object",
  required: ["status"],
  additionalProperties: false,
  properties: {
    status: {
      type: "string",
      enum: ["ok"]
    }
  }
};

pm.test("Status code deve ser 200", function () {
  pm.response.to.have.status(200);
});

pm.test("Resposta deve ser JSON", function () {
  const contentType = pm.response.headers.get("Content-Type") || "";
  pm.expect(contentType).to.include("application/json");
});

pm.test("Schema JSON deve seguir ApiStatusResponse", function () {
  pm.response.to.have.jsonSchema(statusSchema);
});
```

## GET /api/search

```javascript
const productCatalogSchema = {
  type: "array",
  items: {
    type: "object",
    required: ["id", "name", "price", "location"],
    additionalProperties: false,
    properties: {
      id: {
        type: "integer"
      },
      name: {
        type: "string",
        minLength: 1
      },
      price: {
        type: "number",
        minimum: 0
      },
      location: {
        type: "string"
      }
    }
  }
};

pm.test("Status code deve ser 200", function () {
  pm.response.to.have.status(200);
});

pm.test("Resposta deve ser JSON", function () {
  const contentType = pm.response.headers.get("Content-Type") || "";
  pm.expect(contentType).to.include("application/json");
});

pm.test("Schema JSON deve seguir lista de ProductCatalogItem", function () {
  pm.response.to.have.jsonSchema(productCatalogSchema);
});
```

## GET /cart/summary

```javascript
const cartSummarySchema = {
  type: "object",
  required: ["subtotal", "coupon_discount", "progressive_discount", "total"],
  additionalProperties: false,
  properties: {
    subtotal: {
      type: "number",
      minimum: 0
    },
    coupon_discount: {
      type: "number",
      minimum: 0
    },
    progressive_discount: {
      type: "number",
      minimum: 0
    },
    total: {
      type: "number",
      minimum: 0
    }
  }
};

pm.test("Status code deve ser 200", function () {
  pm.response.to.have.status(200);
});

pm.test("Resposta deve ser JSON", function () {
  const contentType = pm.response.headers.get("Content-Type") || "";
  pm.expect(contentType).to.include("application/json");
});

pm.test("Schema JSON deve seguir CartSummary", function () {
  pm.response.to.have.jsonSchema(cartSummarySchema);
});
```

## POST /cart/add

Cenario `200`: envie, por exemplo:

```json
{
  "product_id": 1,
  "quantity": 2
}
```

Cenario `400`: envie `quantity` menor ou igual a zero:

```json
{
  "product_id": 1,
  "quantity": 0
}
```

Script:

```javascript
const cartSummarySchema = {
  type: "object",
  required: ["subtotal", "coupon_discount", "progressive_discount", "total"],
  additionalProperties: false,
  properties: {
    subtotal: {
      type: "number",
      minimum: 0
    },
    coupon_discount: {
      type: "number",
      minimum: 0
    },
    progressive_discount: {
      type: "number",
      minimum: 0
    },
    total: {
      type: "number",
      minimum: 0
    }
  }
};

const errorSchema = {
  type: "object",
  required: ["detail"],
  additionalProperties: false,
  properties: {
    detail: {
      type: "string",
      minLength: 1
    }
  }
};

pm.test("Status code deve ser 200 ou 400 conforme resultado da operacao", function () {
  pm.expect(pm.response.code).to.be.oneOf([200, 400]);
});

pm.test("Resposta deve ser JSON", function () {
  const contentType = pm.response.headers.get("Content-Type") || "";
  pm.expect(contentType).to.include("application/json");
});

if (pm.response.code === 200) {
  pm.test("Schema JSON de sucesso deve seguir CartSummary", function () {
    pm.response.to.have.jsonSchema(cartSummarySchema);
  });
}

if (pm.response.code === 400) {
  pm.test("Schema JSON de erro deve conter detail", function () {
    pm.response.to.have.jsonSchema(errorSchema);
  });

  pm.test("Erro deve indicar quantidade invalida", function () {
    const body = pm.response.json();
    pm.expect(body.detail).to.eql("Quantity must be greater than zero");
  });
}
```

## DELETE /cart/remove/{product_id}

```javascript
const cartSummarySchema = {
  type: "object",
  required: ["subtotal", "coupon_discount", "progressive_discount", "total"],
  additionalProperties: false,
  properties: {
    subtotal: {
      type: "number",
      minimum: 0
    },
    coupon_discount: {
      type: "number",
      minimum: 0
    },
    progressive_discount: {
      type: "number",
      minimum: 0
    },
    total: {
      type: "number",
      minimum: 0
    }
  }
};

pm.test("Status code deve ser 200", function () {
  pm.response.to.have.status(200);
});

pm.test("Resposta deve ser JSON", function () {
  const contentType = pm.response.headers.get("Content-Type") || "";
  pm.expect(contentType).to.include("application/json");
});

pm.test("Schema JSON deve seguir CartSummary", function () {
  pm.response.to.have.jsonSchema(cartSummarySchema);
});
```

## POST /cart/apply-coupon

Cenario `200`: antes desta request, adicione itens suficientes no carrinho para atingir o minimo do cupom. Exemplo de body:

```json
{
  "code": "SAVE10"
}
```

Cenario `400`: use um cupom valido sem subtotal minimo no carrinho, ou envie o codigo vazio:

```json
{
  "code": ""
}
```

Script:

```javascript
const cartSummarySchema = {
  type: "object",
  required: ["subtotal", "coupon_discount", "progressive_discount", "total"],
  additionalProperties: false,
  properties: {
    subtotal: {
      type: "number",
      minimum: 0
    },
    coupon_discount: {
      type: "number",
      minimum: 0
    },
    progressive_discount: {
      type: "number",
      minimum: 0
    },
    total: {
      type: "number",
      minimum: 0
    }
  }
};

const errorSchema = {
  type: "object",
  required: ["detail"],
  additionalProperties: false,
  properties: {
    detail: {
      type: "string",
      minLength: 1
    }
  }
};

const acceptedBusinessErrors = [
  "Coupon code is required",
  "Cart subtotal is below coupon minimum purchase",
  "Coupon is inactive",
  "Coupon is expired"
];

pm.test("Status code deve ser 200 ou 400 conforme resultado da operacao", function () {
  pm.expect(pm.response.code).to.be.oneOf([200, 400]);
});

pm.test("Resposta deve ser JSON", function () {
  const contentType = pm.response.headers.get("Content-Type") || "";
  pm.expect(contentType).to.include("application/json");
});

if (pm.response.code === 200) {
  pm.test("Schema JSON de sucesso deve seguir CartSummary", function () {
    pm.response.to.have.jsonSchema(cartSummarySchema);
  });
}

if (pm.response.code === 400) {
  pm.test("Schema JSON de erro deve conter detail", function () {
    pm.response.to.have.jsonSchema(errorSchema);
  });

  pm.test("Erro deve ser uma falha de regra de negocio esperada", function () {
    const body = pm.response.json();
    pm.expect(acceptedBusinessErrors).to.include(body.detail);
  });
}
```

## DELETE /cart/coupon

```javascript
const cartSummarySchema = {
  type: "object",
  required: ["subtotal", "coupon_discount", "progressive_discount", "total"],
  additionalProperties: false,
  properties: {
    subtotal: {
      type: "number",
      minimum: 0
    },
    coupon_discount: {
      type: "number",
      minimum: 0
    },
    progressive_discount: {
      type: "number",
      minimum: 0
    },
    total: {
      type: "number",
      minimum: 0
    }
  }
};

pm.test("Status code deve ser 200", function () {
  pm.response.to.have.status(200);
});

pm.test("Resposta deve ser JSON", function () {
  const contentType = pm.response.headers.get("Content-Type") || "";
  pm.expect(contentType).to.include("application/json");
});

pm.test("Schema JSON deve seguir CartSummary", function () {
  pm.response.to.have.jsonSchema(cartSummarySchema);
});
```
