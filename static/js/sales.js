document.addEventListener("DOMContentLoaded", function () {
  // =====================================================
  // ELEMENTS
  // =====================================================

  const brandSelect = document.getElementById("brand");
  const productSelect = document.getElementById("product");
  const variantSelect = document.getElementById("variant");

  const imeiSearch = document.getElementById("imeiSearch");
  const imeiInput = document.getElementById("imei");
  const imeiResults = document.getElementById("imeiSearchResults");
  const selectedImeiText = document.getElementById("selectedImeiText");

  const referencePrice = document.getElementById("referencePrice");
  const sellingPrice = document.getElementById("sellingPrice");

  const negotiatedPriceButton = document.getElementById(
    "enableNegotiatedPrice",
  );

  const addItemButton = document.getElementById("addItem");

  let availableIMEIs = [];
  let selectedIMEI = null;

  // True only when cashier explicitly clicks Negotiated Price.
  let negotiatedPriceApproved = false;

  // =====================================================
  // HELPERS
  // =====================================================

  function resetSelect(select, placeholder) {
    if (!select) return;

    select.innerHTML = `<option value="">${placeholder}</option>`;
  }

  function formatMoney(amount) {
    const number = Number(amount) || 0;

    return number.toLocaleString();
  }

  // =====================================================
  // RESET IMEI
  // =====================================================

  function resetIMEI() {
    availableIMEIs = [];
    selectedIMEI = null;

    if (imeiInput) {
      imeiInput.value = "";
    }

    if (imeiSearch) {
      imeiSearch.value = "";
      imeiSearch.disabled = true;

      imeiSearch.placeholder = "Type last digits...";
    }

    if (imeiResults) {
      imeiResults.innerHTML = "";
    }

    if (selectedImeiText) {
      selectedImeiText.textContent = "Select a variant first";

      selectedImeiText.className = "text-muted";
    }
  }

  // =====================================================
  // RESET PRICE
  // =====================================================

  function resetPrice() {
    negotiatedPriceApproved = false;

    if (referencePrice) {
      referencePrice.textContent = "Select variant";
    }

    if (sellingPrice) {
      sellingPrice.value = "";

      sellingPrice.placeholder = "Select variant first";

      /*
       * When the Negotiated Price button exists,
       * global price override is OFF.
       *
       * Therefore the field must return to locked.
       */
      if (negotiatedPriceButton) {
        sellingPrice.readOnly = true;
      }
    }

    if (negotiatedPriceButton) {
      negotiatedPriceButton.innerHTML =
        '<i class="fas fa-handshake"></i> Negotiated Price';

      negotiatedPriceButton.classList.remove("btn-outline-success");

      negotiatedPriceButton.classList.add("btn-outline-warning");
    }
  }

  // =====================================================
  // RESET ENTIRE ADD PRODUCT AREA
  // =====================================================

  function resetProductForm() {
    brandSelect.value = "";

    resetSelect(productSelect, "Select Product");

    resetSelect(variantSelect, "Select Variant");

    resetIMEI();
    resetPrice();
  }

  // =====================================================
  // LOAD PRODUCTS
  // =====================================================

  async function loadProducts(brandId) {
    resetSelect(productSelect, "Select Product");

    resetSelect(variantSelect, "Select Variant");

    resetIMEI();
    resetPrice();

    if (!brandId) return;

    try {
      const response = await fetch(`/sales/api/products/${brandId}`);

      if (!response.ok) {
        throw new Error("Unable to load products.");
      }

      const products = await response.json();

      products.forEach((product) => {
        const option = document.createElement("option");

        option.value = product.id;
        option.textContent = product.name;

        productSelect.appendChild(option);
      });
    } catch (error) {
      console.error(error);

      alert("Unable to load products.");
    }
  }

  // =====================================================
  // LOAD VARIANTS
  // =====================================================

  async function loadVariants(productId) {
    resetSelect(variantSelect, "Select Variant");

    resetIMEI();
    resetPrice();

    if (!productId) return;

    try {
      const response = await fetch(`/sales/api/variants/${productId}`);

      if (!response.ok) {
        throw new Error("Unable to load variants.");
      }

      const variants = await response.json();

      variants.forEach((variant) => {
        const option = document.createElement("option");

        option.value = variant.id;

        const details = [variant.storage, variant.ram, variant.colour]
          .filter(Boolean)
          .join(" / ");

        option.textContent = details
          ? `${variant.sku} (${details})`
          : variant.sku;

        option.dataset.price = variant.price;

        option.dataset.stock = variant.stock;

        option.dataset.brand = variant.brand;

        option.dataset.product = variant.product;

        option.dataset.storage = variant.storage || "";

        option.dataset.ram = variant.ram || "";

        option.dataset.colour = variant.colour || "";

        variantSelect.appendChild(option);
      });
    } catch (error) {
      console.error(error);

      alert("Unable to load product variants.");
    }
  }

  // =====================================================
  // LOAD IMEIS
  // =====================================================

  async function loadIMEIs(variantId) {
    resetIMEI();

    if (!variantId) {
      return;
    }

    selectedImeiText.textContent = "Loading available IMEIs...";

    try {
      const response = await fetch(`/sales/api/imeis/${variantId}`);

      if (!response.ok) {
        throw new Error("Unable to load IMEIs.");
      }

      availableIMEIs = await response.json();

      if (availableIMEIs.length === 0) {
        imeiSearch.disabled = true;

        selectedImeiText.textContent = "No available IMEIs for this variant";

        selectedImeiText.className = "text-danger";

        return;
      }

      imeiSearch.disabled = false;

      imeiSearch.placeholder = "Type last digits of IMEI...";

      selectedImeiText.textContent = `${availableIMEIs.length} IMEI(s) available — type the last digits`;

      selectedImeiText.className = "text-muted";

      imeiSearch.focus();
    } catch (error) {
      console.error(error);

      selectedImeiText.textContent = "Unable to load IMEIs";

      selectedImeiText.className = "text-danger";
    }
  }

  // =====================================================
  // SELECT EXACT IMEI
  // =====================================================

  function selectIMEI(imei) {
    selectedIMEI = imei;

    imeiInput.value = imei.id;

    imeiSearch.value = imei.imei;

    imeiResults.innerHTML = "";

    selectedImeiText.textContent = `Selected: ${imei.imei}`;

    selectedImeiText.className = "text-success fw-semibold";
  }

  // =====================================================
  // SEARCH IMEI BY ENDING DIGITS
  // =====================================================

  function searchIMEIs(searchValue) {
    imeiResults.innerHTML = "";

    selectedIMEI = null;
    imeiInput.value = "";

    const search = searchValue.trim();

    if (!search) {
      selectedImeiText.textContent = `${availableIMEIs.length} IMEI(s) available — type the last digits`;

      selectedImeiText.className = "text-muted";

      return;
    }

    const matches = availableIMEIs.filter((item) =>
      String(item.imei).endsWith(search),
    );

    // NO MATCH

    if (matches.length === 0) {
      selectedImeiText.textContent = "No matching IMEI";

      selectedImeiText.className = "text-danger";

      return;
    }

    // EXACTLY ONE MATCH

    if (matches.length === 1) {
      selectIMEI(matches[0]);

      return;
    }

    // MULTIPLE MATCHES

    selectedImeiText.textContent = `${matches.length} matching IMEIs — type more digits`;

    selectedImeiText.className = "text-warning";

    matches.slice(0, 10).forEach((imei) => {
      const button = document.createElement("button");

      button.type = "button";

      button.className = "list-group-item list-group-item-action";

      button.textContent = imei.imei;

      button.addEventListener("click", function () {
        selectIMEI(imei);
      });

      imeiResults.appendChild(button);
    });
  }

  // =====================================================
  // BRAND CHANGE
  // =====================================================

  if (brandSelect) {
    brandSelect.addEventListener("change", function () {
      loadProducts(this.value);
    });
  }

  // =====================================================
  // PRODUCT CHANGE
  // =====================================================

  if (productSelect) {
    productSelect.addEventListener("change", function () {
      loadVariants(this.value);
    });
  }

  // =====================================================
  // VARIANT CHANGE
  // =====================================================

  if (variantSelect) {
    variantSelect.addEventListener("change", function () {
      resetIMEI();
      resetPrice();

      if (!this.value) {
        return;
      }

      const selectedVariant = this.options[this.selectedIndex];

      const price = Number(selectedVariant.dataset.price) || 0;

      // -----------------------------------------
      // REFERENCE PRICE
      // -----------------------------------------

      referencePrice.textContent = `UGX ${formatMoney(price)}`;

      // -----------------------------------------
      // ACTUAL PRICE STARTS AT VARIANT PRICE
      // -----------------------------------------

      sellingPrice.value = price;

      sellingPrice.placeholder = "Enter actual selling price";

      /*
       * If Negotiated Price button exists,
       * global override is disabled.
       *
       * Keep actual price locked until
       * cashier explicitly approves negotiation.
       */
      if (negotiatedPriceButton) {
        sellingPrice.readOnly = true;
      } else {
        /*
         * Global price override enabled.
         */
        sellingPrice.readOnly = false;
      }

      loadIMEIs(this.value);
    });
  }

  // =====================================================
  // IMEI SEARCH
  // =====================================================

  if (imeiSearch) {
    imeiSearch.addEventListener("input", function () {
      searchIMEIs(this.value);
    });
  }

  // =====================================================
  // NEGOTIATED PRICE BUTTON
  // =====================================================

  if (negotiatedPriceButton) {
    negotiatedPriceButton.addEventListener("click", function () {
      if (!variantSelect.value) {
        alert("Please select a variant first.");

        return;
      }

      negotiatedPriceApproved = true;

      sellingPrice.readOnly = false;

      sellingPrice.focus();

      sellingPrice.select();

      negotiatedPriceButton.innerHTML =
        '<i class="fas fa-check"></i> Negotiation Approved';

      negotiatedPriceButton.classList.remove("btn-outline-warning");

      negotiatedPriceButton.classList.add("btn-outline-success");
    });
  }

  // =====================================================
  // ADD ITEM TO CART
  // =====================================================

  if (addItemButton) {
    addItemButton.addEventListener("click", function () {
      // -----------------------------------------
      // BRAND
      // -----------------------------------------

      if (!brandSelect.value) {
        alert("Please select a brand.");

        return;
      }

      // -----------------------------------------
      // PRODUCT
      // -----------------------------------------

      if (!productSelect.value) {
        alert("Please select a product.");

        return;
      }

      // -----------------------------------------
      // VARIANT
      // -----------------------------------------

      if (!variantSelect.value) {
        alert("Please select a variant.");

        return;
      }

      // -----------------------------------------
      // IMEI
      // -----------------------------------------

      if (!selectedIMEI) {
        alert(
          "Please enter the IMEI ending digits until one exact IMEI is selected.",
        );

        imeiSearch.focus();

        return;
      }

      const selectedVariant =
        variantSelect.options[variantSelect.selectedIndex];

      // -----------------------------------------
      // SELLING PRICE
      // -----------------------------------------

      const price = Number(sellingPrice.value);

      if (!Number.isFinite(price) || price <= 0) {
        alert("Please enter a valid selling price.");

        sellingPrice.focus();

        return;
      }

      // -----------------------------------------
      // STANDARD VARIANT PRICE
      // -----------------------------------------

      const standardPrice = Number(selectedVariant.dataset.price) || 0;

      /*
       * Extra browser-side protection:
       *
       * If global override is disabled and
       * negotiation was NOT approved, the
       * price must remain the variant price.
       */
      if (
        negotiatedPriceButton &&
        !negotiatedPriceApproved &&
        price !== standardPrice
      ) {
        alert("Click Negotiated Price before changing the selling price.");

        return;
      }

      // -----------------------------------------
      // PRODUCT DISPLAY NAME
      // -----------------------------------------

      const productName =
        selectedVariant.dataset.product ||
        productSelect.options[productSelect.selectedIndex].text;

      const details = [
        selectedVariant.dataset.storage,
        selectedVariant.dataset.ram,
        selectedVariant.dataset.colour,
      ]
        .filter(Boolean)
        .join(" / ");

      const productDisplay = details
        ? `${productName} - ${details}`
        : productName;

      // -----------------------------------------
      // ONE IMEI = ONE DEVICE
      // -----------------------------------------

      const quantity = 1;

      // -----------------------------------------
      // ADD TO CART
      // -----------------------------------------

      addToCart({
        variant_id: variantSelect.value,

        imei_id: selectedIMEI.id,

        product: productDisplay,

        imei: selectedIMEI.imei,

        quantity: quantity,

        price: price,

        standard_price: standardPrice,

        price_override: negotiatedPriceApproved || !negotiatedPriceButton,

        total: price,
      });

      // =========================================
      // RESET ADD PRODUCT SECTION
      // =========================================

      resetProductForm();
    });
  }
});

// ==========================================================
// CUSTOMER SEARCH
// ==========================================================

const customerSearch = document.getElementById("customerSearch");

const customerResults = document.getElementById("customerSearchResults");

const customerId = document.getElementById("customer_id");

if (customerSearch) {
  customerSearch.addEventListener("keyup", async function () {
    const q = this.value.trim();

    customerResults.innerHTML = "";

    customerId.value = "";

    if (q.length < 2) return;

    const response = await fetch(
      `/customers/api/search?q=${encodeURIComponent(q)}`,
    );

    const customers = await response.json();

    customers.forEach((customer) => {
      const item = document.createElement("a");

      item.href = "#";

      item.className = "list-group-item list-group-item-action";

      item.innerHTML = `

                <strong>${customer.name}</strong><br>

                <small>${customer.code} • ${customer.phone}</small>

            `;

      item.onclick = function (e) {
        e.preventDefault();

        customerSearch.value = `${customer.name} (${customer.phone})`;

        customerId.value = customer.id;

        document.getElementById("customer_name").value = customer.name;

        document.getElementById("customer_phone").value = customer.phone;

        customerResults.innerHTML = "";
      };

      customerResults.appendChild(item);
    });
  });
}

// ==========================================================
// REGISTER NEW CUSTOMER
// ==========================================================

// ==========================================================
// REGISTER NEW CUSTOMER FROM SALES POS
// ==========================================================

const newCustomerBtn =
  document.getElementById("newCustomerBtn");

if (newCustomerBtn) {
  newCustomerBtn.addEventListener("click", function () {

    window.location.href =
      "/customers/create?return_to=sale";

  });
}


/* ==========================================================
   MINIFY V2 FAST BARCODE POS
   Hardware scanners act as keyboard input and terminate with Enter.
========================================================== */
(() => {
  const scanner = document.getElementById("barcodeScanner");
  const status = document.getElementById("barcodeStatus");
  const payment = document.querySelector('select[name="payment_method"]');
  const creditFields = document.getElementById("creditFields");
  const amountPaid = document.getElementById("amountPaid");
  const grandTotal = document.getElementById("grandTotal");
  const cameraBtn = document.getElementById("cameraScanBtn");

  async function barcodeLookup(code) {
    if (!code) return;
    if (status) status.textContent = "Looking up barcode...";
    try {
      const response = await fetch(`/sales/api/barcode/${encodeURIComponent(code)}`);
      if (!response.ok) throw new Error("Barcode not found");
      const v = await response.json();

      if (Number(v.stock) <= 0) {
        if (status) status.textContent = "Product is out of stock.";
        alert("This product is out of stock.");
        return;
      }

      const brand = document.getElementById("brand");
      const product = document.getElementById("product");
      const variant = document.getElementById("variant");

      if (brand && v.brand_id) {
        brand.value = String(v.brand_id);
        brand.dispatchEvent(new Event("change"));
      }

      // Populate product directly so the existing POS can continue normally.
      if (product) {
        product.innerHTML = `<option value="${v.product_id}">${v.product}</option>`;
        product.value = String(v.product_id);
        product.dispatchEvent(new Event("change"));
      }

      // Populate the exact variant without waiting for another network call.
      if (variant) {
        const option = document.createElement("option");
        option.value = String(v.id);
        option.textContent = `${v.sku} (${[v.storage, v.ram, v.colour].filter(Boolean).join(" / ")})`;
        option.dataset.price = v.price;
        option.dataset.stock = v.stock;
        option.dataset.brand = v.brand;
        option.dataset.product = v.product;
        option.dataset.storage = v.storage || "";
        option.dataset.ram = v.ram || "";
        option.dataset.colour = v.colour || "";

        variant.innerHTML = "";
        variant.appendChild(option);
        variant.value = String(v.id);
        variant.dispatchEvent(new Event("change"));
      }

      if (status) status.textContent = `Scanned: ${v.sku} — select the IMEI if required, then Add To Cart.`;
      scanner.value = "";
    } catch (err) {
      if (status) status.textContent = "Barcode not found.";
      alert(`No active product variant matches barcode "${code}".`);
      scanner.focus();
    }
  }

  scanner?.addEventListener("keydown", e => {
    if (e.key === "Enter") {
      e.preventDefault();
      barcodeLookup(scanner.value.trim());
    }
  });

  payment?.addEventListener("change", () => {
    const credit = payment.value === "Credit" || payment.value === "Installment";
    creditFields?.classList.toggle("d-none", !credit);
    if (!credit && amountPaid) amountPaid.value = "";
  });

  cameraBtn?.addEventListener("click", async () => {
    if (!("BarcodeDetector" in window)) {
      alert("Camera barcode scanning is not supported by this browser. Use a USB/Bluetooth scanner instead.");
      return;
    }
    try {
      const detector = new BarcodeDetector({formats: ["code_128","ean_13","ean_8","upc_a","upc_e"]});
      const stream = await navigator.mediaDevices.getUserMedia({video: {facingMode: "environment"}});
      const video = document.createElement("video");
      video.autoplay = true; video.playsInline = true; video.style.cssText =
        "position:fixed;inset:12%;width:76%;max-height:76%;z-index:9999;background:#000;border-radius:12px";
      document.body.appendChild(video);
      video.srcObject = stream;
      const close = () => { stream.getTracks().forEach(t => t.stop()); video.remove(); };
      const timer = setInterval(async () => {
        try {
          const codes = await detector.detect(video);
          if (codes.length) {
            clearInterval(timer); close(); barcodeLookup(codes[0].rawValue);
          }
        } catch (_) {}
      }, 250);
      setTimeout(() => { clearInterval(timer); close(); }, 30000);
    } catch (err) {
      alert("Camera access could not be started. Check browser camera permission.");
    }
  });
})();
