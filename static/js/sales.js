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

    const negotiatedPriceButton =
        document.getElementById("enableNegotiatedPrice");

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

        select.innerHTML =
            `<option value="">${placeholder}</option>`;
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

            imeiSearch.placeholder =
                "Type last digits...";
        }

        if (imeiResults) {
            imeiResults.innerHTML = "";
        }

        if (selectedImeiText) {

            selectedImeiText.textContent =
                "Select a variant first";

            selectedImeiText.className =
                "text-muted";
        }
    }


    // =====================================================
    // RESET PRICE
    // =====================================================

    function resetPrice() {

        negotiatedPriceApproved = false;

        if (referencePrice) {
            referencePrice.textContent =
                "Select variant";
        }

        if (sellingPrice) {

            sellingPrice.value = "";

            sellingPrice.placeholder =
                "Select variant first";

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

            negotiatedPriceButton.classList.remove(
                "btn-outline-success"
            );

            negotiatedPriceButton.classList.add(
                "btn-outline-warning"
            );
        }
    }


    // =====================================================
    // RESET ENTIRE ADD PRODUCT AREA
    // =====================================================

    function resetProductForm() {

        brandSelect.value = "";

        resetSelect(
            productSelect,
            "Select Product"
        );

        resetSelect(
            variantSelect,
            "Select Variant"
        );

        resetIMEI();
        resetPrice();
    }


    // =====================================================
    // LOAD PRODUCTS
    // =====================================================

    async function loadProducts(brandId) {

        resetSelect(
            productSelect,
            "Select Product"
        );

        resetSelect(
            variantSelect,
            "Select Variant"
        );

        resetIMEI();
        resetPrice();

        if (!brandId) return;

        try {

            const response = await fetch(
                `/sales/api/products/${brandId}`
            );

            if (!response.ok) {
                throw new Error(
                    "Unable to load products."
                );
            }

            const products =
                await response.json();

            products.forEach(product => {

                const option =
                    document.createElement("option");

                option.value = product.id;
                option.textContent = product.name;

                productSelect.appendChild(option);
            });

        } catch (error) {

            console.error(error);

            alert(
                "Unable to load products."
            );
        }
    }


    // =====================================================
    // LOAD VARIANTS
    // =====================================================

    async function loadVariants(productId) {

        resetSelect(
            variantSelect,
            "Select Variant"
        );

        resetIMEI();
        resetPrice();

        if (!productId) return;

        try {

            const response = await fetch(
                `/sales/api/variants/${productId}`
            );

            if (!response.ok) {
                throw new Error(
                    "Unable to load variants."
                );
            }

            const variants =
                await response.json();

            variants.forEach(variant => {

                const option =
                    document.createElement("option");

                option.value = variant.id;

                const details = [
                    variant.storage,
                    variant.ram,
                    variant.colour
                ]
                    .filter(Boolean)
                    .join(" / ");

                option.textContent =
                    details
                        ? `${variant.sku} (${details})`
                        : variant.sku;

                option.dataset.price =
                    variant.price;

                option.dataset.stock =
                    variant.stock;

                option.dataset.brand =
                    variant.brand;

                option.dataset.product =
                    variant.product;

                option.dataset.storage =
                    variant.storage || "";

                option.dataset.ram =
                    variant.ram || "";

                option.dataset.colour =
                    variant.colour || "";

                variantSelect.appendChild(
                    option
                );
            });

        } catch (error) {

            console.error(error);

            alert(
                "Unable to load product variants."
            );
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

        selectedImeiText.textContent =
            "Loading available IMEIs...";

        try {

            const response = await fetch(
                `/sales/api/imeis/${variantId}`
            );

            if (!response.ok) {
                throw new Error(
                    "Unable to load IMEIs."
                );
            }

            availableIMEIs =
                await response.json();

            if (availableIMEIs.length === 0) {

                imeiSearch.disabled = true;

                selectedImeiText.textContent =
                    "No available IMEIs for this variant";

                selectedImeiText.className =
                    "text-danger";

                return;
            }

            imeiSearch.disabled = false;

            imeiSearch.placeholder =
                "Type last digits of IMEI...";

            selectedImeiText.textContent =
                `${availableIMEIs.length} IMEI(s) available — type the last digits`;

            selectedImeiText.className =
                "text-muted";

            imeiSearch.focus();

        } catch (error) {

            console.error(error);

            selectedImeiText.textContent =
                "Unable to load IMEIs";

            selectedImeiText.className =
                "text-danger";
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

        selectedImeiText.textContent =
            `Selected: ${imei.imei}`;

        selectedImeiText.className =
            "text-success fw-semibold";
    }


    // =====================================================
    // SEARCH IMEI BY ENDING DIGITS
    // =====================================================

    function searchIMEIs(searchValue) {

        imeiResults.innerHTML = "";

        selectedIMEI = null;
        imeiInput.value = "";

        const search =
            searchValue.trim();

        if (!search) {

            selectedImeiText.textContent =
                `${availableIMEIs.length} IMEI(s) available — type the last digits`;

            selectedImeiText.className =
                "text-muted";

            return;
        }

        const matches =
            availableIMEIs.filter(item =>
                String(item.imei)
                    .endsWith(search)
            );


        // NO MATCH

        if (matches.length === 0) {

            selectedImeiText.textContent =
                "No matching IMEI";

            selectedImeiText.className =
                "text-danger";

            return;
        }


        // EXACTLY ONE MATCH

        if (matches.length === 1) {

            selectIMEI(
                matches[0]
            );

            return;
        }


        // MULTIPLE MATCHES

        selectedImeiText.textContent =
            `${matches.length} matching IMEIs — type more digits`;

        selectedImeiText.className =
            "text-warning";


        matches
            .slice(0, 10)
            .forEach(imei => {

                const button =
                    document.createElement("button");

                button.type = "button";

                button.className =
                    "list-group-item list-group-item-action";

                button.textContent =
                    imei.imei;

                button.addEventListener(
                    "click",
                    function () {

                        selectIMEI(
                            imei
                        );
                    }
                );

                imeiResults.appendChild(
                    button
                );
            });
    }


    // =====================================================
    // BRAND CHANGE
    // =====================================================

    if (brandSelect) {

        brandSelect.addEventListener(
            "change",
            function () {

                loadProducts(
                    this.value
                );
            }
        );
    }


    // =====================================================
    // PRODUCT CHANGE
    // =====================================================

    if (productSelect) {

        productSelect.addEventListener(
            "change",
            function () {

                loadVariants(
                    this.value
                );
            }
        );
    }


    // =====================================================
    // VARIANT CHANGE
    // =====================================================

    if (variantSelect) {

        variantSelect.addEventListener(
            "change",
            function () {

                resetIMEI();
                resetPrice();

                if (!this.value) {
                    return;
                }

                const selectedVariant =
                    this.options[
                        this.selectedIndex
                    ];

                const price =
                    Number(
                        selectedVariant.dataset.price
                    ) || 0;


                // -----------------------------------------
                // REFERENCE PRICE
                // -----------------------------------------

                referencePrice.textContent =
                    `UGX ${formatMoney(price)}`;


                // -----------------------------------------
                // ACTUAL PRICE STARTS AT VARIANT PRICE
                // -----------------------------------------

                sellingPrice.value =
                    price;

                sellingPrice.placeholder =
                    "Enter actual selling price";


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


                loadIMEIs(
                    this.value
                );
            }
        );
    }


    // =====================================================
    // IMEI SEARCH
    // =====================================================

    if (imeiSearch) {

        imeiSearch.addEventListener(
            "input",
            function () {

                searchIMEIs(
                    this.value
                );
            }
        );
    }


    // =====================================================
    // NEGOTIATED PRICE BUTTON
    // =====================================================

    if (negotiatedPriceButton) {

        negotiatedPriceButton.addEventListener(
            "click",
            function () {

                if (!variantSelect.value) {

                    alert(
                        "Please select a variant first."
                    );

                    return;
                }


                negotiatedPriceApproved = true;

                sellingPrice.readOnly = false;

                sellingPrice.focus();

                sellingPrice.select();


                negotiatedPriceButton.innerHTML =
                    '<i class="fas fa-check"></i> Negotiation Approved';

                negotiatedPriceButton.classList.remove(
                    "btn-outline-warning"
                );

                negotiatedPriceButton.classList.add(
                    "btn-outline-success"
                );
            }
        );
    }


    // =====================================================
    // ADD ITEM TO CART
    // =====================================================

    if (addItemButton) {

        addItemButton.addEventListener(
            "click",
            function () {


                // -----------------------------------------
                // BRAND
                // -----------------------------------------

                if (!brandSelect.value) {

                    alert(
                        "Please select a brand."
                    );

                    return;
                }


                // -----------------------------------------
                // PRODUCT
                // -----------------------------------------

                if (!productSelect.value) {

                    alert(
                        "Please select a product."
                    );

                    return;
                }


                // -----------------------------------------
                // VARIANT
                // -----------------------------------------

                if (!variantSelect.value) {

                    alert(
                        "Please select a variant."
                    );

                    return;
                }


                // -----------------------------------------
                // IMEI
                // -----------------------------------------

                if (!selectedIMEI) {

                    alert(
                        "Please enter the IMEI ending digits until one exact IMEI is selected."
                    );

                    imeiSearch.focus();

                    return;
                }


                const selectedVariant =
                    variantSelect.options[
                        variantSelect.selectedIndex
                    ];


                // -----------------------------------------
                // SELLING PRICE
                // -----------------------------------------

                const price =
                    Number(
                        sellingPrice.value
                    );


                if (
                    !Number.isFinite(price) ||
                    price <= 0
                ) {

                    alert(
                        "Please enter a valid selling price."
                    );

                    sellingPrice.focus();

                    return;
                }


                // -----------------------------------------
                // STANDARD VARIANT PRICE
                // -----------------------------------------

                const standardPrice =
                    Number(
                        selectedVariant.dataset.price
                    ) || 0;


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

                    alert(
                        "Click Negotiated Price before changing the selling price."
                    );

                    return;
                }


                // -----------------------------------------
                // PRODUCT DISPLAY NAME
                // -----------------------------------------

                const productName =
                    selectedVariant.dataset.product
                    ||
                    productSelect.options[
                        productSelect.selectedIndex
                    ].text;


                const details = [
                    selectedVariant.dataset.storage,
                    selectedVariant.dataset.ram,
                    selectedVariant.dataset.colour
                ]
                    .filter(Boolean)
                    .join(" / ");


                const productDisplay =
                    details
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

                    variant_id:
                        variantSelect.value,

                    imei_id:
                        selectedIMEI.id,

                    product:
                        productDisplay,

                    imei:
                        selectedIMEI.imei,

                    quantity:
                        quantity,

                    price:
                        price,

                    standard_price:
                        standardPrice,

                    price_override:
                        negotiatedPriceApproved ||
                        !negotiatedPriceButton,

                    total:
                        price
                });


                // =========================================
                // RESET ADD PRODUCT SECTION
                // =========================================

                resetProductForm();
            }
        );
    }

});