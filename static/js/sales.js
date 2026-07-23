document.addEventListener("DOMContentLoaded", function () {
  // -----------------------------------
  // Dropdowns
  // -----------------------------------
  const brandSelect = document.getElementById("brand");
  const productSelect = document.getElementById("product");
  const variantSelect = document.getElementById("variant");
  const imeiSelect = document.getElementById("imei");
  const addItemButton = document.getElementById("addItem");

  // -----------------------------------
  // Load Products
  // -----------------------------------
  brandSelect.addEventListener("change", function () {
    loadProducts(this.value, productSelect, variantSelect, imeiSelect);
  });

  // -----------------------------------
  // Load Variants
  // -----------------------------------
  productSelect.addEventListener("change", function () {
    loadVariants(this.value, variantSelect, imeiSelect);
  });

  // -----------------------------------
  // Load IMEIs
  // -----------------------------------
  variantSelect.addEventListener("change", function () {
    loadIMEIs(this.value, imeiSelect);
  });

  // -----------------------------------
  // Add To Cart
  // -----------------------------------
  addItemButton.addEventListener("click", function () {
    if (productSelect.value === "") {
      alert("Please select a product.");
      return;
    }

    if (variantSelect.value === "") {
      alert("Please select a variant.");
      return;
    }

    const productText = productSelect.options[productSelect.selectedIndex].text;

    const imeiText =
      imeiSelect.value !== ""
        ? imeiSelect.options[imeiSelect.selectedIndex].text
        : "-";

    const quantity = parseInt(
      document.querySelector("input[name='quantity']").value,
    );

    // Temporary price
    // We'll replace this with the real selling price later.
    const selectedVariant = variantSelect.options[variantSelect.selectedIndex];

    const price = parseFloat(selectedVariant.dataset.price);

    const stock = parseInt(selectedVariant.dataset.stock);

    if (quantity > stock) {
      alert(`Only ${stock} item(s) available in stock.`);

      return;
    }

    const total = quantity * price;

    addToCart({
      variant_id: variantSelect.value,

      imei_id: imeiSelect.value,

      product: productText,

      imei: imeiText,

      quantity: quantity,

      price: price,

      total: total,
    });
  });
});
