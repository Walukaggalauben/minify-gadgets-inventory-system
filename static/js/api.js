// -----------------------------
// Helper Function
// -----------------------------
function resetSelect(select, placeholder) {
    select.innerHTML = `<option value="">${placeholder}</option>`;
}

// -----------------------------
// Load Products
// -----------------------------
function loadProducts(brandId, productSelect, variantSelect, imeiSelect) {

    resetSelect(productSelect, "Select Product");
    resetSelect(variantSelect, "Select Variant");
    resetSelect(imeiSelect, "Select IMEI");

    if (!brandId) return;

    fetch(`/sales/api/products/${brandId}`)
        .then(response => response.json())
        .then(products => {

            products.forEach(product => {

                const option = document.createElement("option");

                option.value = product.id;
                option.textContent = product.name;

                productSelect.appendChild(option);

            });

        })
        .catch(error => console.error(error));

}

// -----------------------------
// Load Variants
// -----------------------------
async function loadVariants(productId, variantSelect, imeiSelect) {

    variantSelect.innerHTML =
        '<option value="">Select Variant</option>';

    imeiSelect.innerHTML =
        '<option value="">Select IMEI</option>';

    if (!productId) return;

    const response = await fetch(`/sales/api/variants/${productId}`);

    const variants = await response.json();

    variants.forEach(variant => {

        const option = document.createElement("option");

        option.value = variant.id;

        option.text =
            `${variant.sku} (${variant.storage}/${variant.ram})`;

        // Store additional information
        option.dataset.price = variant.price;
        option.dataset.stock = variant.stock;

        variantSelect.appendChild(option);

    });

}

// -----------------------------
// Load IMEIs
// -----------------------------
function loadIMEIs(variantId, imeiSelect) {

    resetSelect(imeiSelect, "Select IMEI");

    if (!variantId) return;

    fetch(`/sales/api/imeis/${variantId}`)
        .then(response => response.json())
        .then(imeis => {

            imeis.forEach(imei => {

                const option = document.createElement("option");

                option.value = imei.id;
                option.textContent = imei.imei;

                imeiSelect.appendChild(option);

            });

        })
        .catch(error => console.error(error));

}