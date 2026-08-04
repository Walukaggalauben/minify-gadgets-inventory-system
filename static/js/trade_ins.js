document.addEventListener("DOMContentLoaded", () => {

    // =====================================================
    // WIZARD NAVIGATION
    // =====================================================

    const steps = document.querySelectorAll(".wizard-step");
    const navLinks = document.querySelectorAll("#tradeWizard .nav-link");

    let currentStep = 0;

    function showStep(index) {

        steps.forEach((step, i) => {

            step.classList.toggle("active-step", i === index);
            step.classList.toggle("d-none", i !== index);

        });

        navLinks.forEach((nav, i) => {

            nav.classList.toggle("active", i === index);

        });

        currentStep = index;

        updateReview();

    }

    document.querySelectorAll(".nextStep").forEach(btn => {

        btn.addEventListener("click", () => {

            if (currentStep < steps.length - 1) {

                showStep(currentStep + 1);

            }

        });

    });

    document.querySelectorAll(".prevStep").forEach(btn => {

        btn.addEventListener("click", () => {

            if (currentStep > 0) {

                showStep(currentStep - 1);

            }

        });

    });

    showStep(0);

    // =====================================================
    // ELEMENTS
    // =====================================================

    const tradeValue =
        document.querySelector(".finalTradeValue");

    const sellingPrice =
        document.querySelector(".sellingPrice");

    const expectedProfit =
        document.getElementById("expectedProfit");

    const battery =
        document.querySelector(
            'input[name="battery_health[]"]'
        );

    const buyRadio =
        document.getElementById("buyPhone");

    const swapRadio =
        document.getElementById("swapPhone");

    const buySection =
        document.getElementById("buySection");

    const swapSection =
        document.getElementById("swapSection");

    const swapSellingPrice =
        document.getElementById("swapSellingPrice");

    const customerTopup =
        document.getElementById("customerTopup");

    // =====================================================
    // BUY / SWAP SWITCHING
    // =====================================================

    function updateTradeMode() {

        if (!buyRadio || !swapRadio)
            return;

        if (buyRadio.checked) {

            buySection.style.display = "block";

            swapSection.style.display = "none";

        }

        if (swapRadio.checked) {

            buySection.style.display = "none";

            swapSection.style.display = "block";

        }

        calculateProfit();

    }

    buyRadio?.addEventListener(
        "change",
        updateTradeMode
    );

    swapRadio?.addEventListener(
        "change",
        updateTradeMode
    );

    updateTradeMode();

    // =====================================================
    // PROFIT
    // =====================================================

    function calculateProfit() {

        if (!tradeValue || !expectedProfit)
            return;

        let selling = 0;

        if (buyRadio && buyRadio.checked) {

            selling =
                parseFloat(sellingPrice?.value) || 0;

        }

        if (swapRadio && swapRadio.checked) {

            selling =
                parseFloat(swapSellingPrice?.value) || 0;

        }

        const buying =
            parseFloat(tradeValue.value) || 0;

        const profit =
            selling - buying;

        expectedProfit.value =
            "UGX " +
            profit.toLocaleString();

        calculateTopup();

    }

    tradeValue?.addEventListener(
        "input",
        calculateProfit
    );

    sellingPrice?.addEventListener(
        "input",
        calculateProfit
    );

    swapSellingPrice?.addEventListener(
        "input",
        calculateProfit
    );

    // =====================================================
    // TOP-UP CALCULATION
    // =====================================================

    function calculateTopup() {

        if (!swapRadio?.checked)
            return;

        const selling =
            parseFloat(swapSellingPrice.value) || 0;

        const trade =
            parseFloat(tradeValue.value) || 0;

        const difference =
            selling - trade;

        if (difference > 0) {

            customerTopup.value = difference;

        }

        else {

            customerTopup.value = 0;

        }

    }

    // =====================================================
    // BATTERY WARNING
    // =====================================================

    battery?.addEventListener(
        "change",
        function () {

            const value =
                parseInt(this.value) || 0;

            if (
                value > 0 &&
                value < 80
            ) {

                alert(
                    "Battery health is below 80%. Consider lowering the trade value."
                );

            }

        }
    );

    // =====================================================
    // IMEI VALIDATION
    // =====================================================

    document.querySelectorAll(".imeiInput").forEach(input => {

        input.addEventListener("blur", function () {

            const imei =
                this.value.trim();

            if (
                imei &&
                !/^\d{15}$/.test(imei)
            ) {

                alert(
                    "IMEI must contain exactly 15 digits."
                );

                this.focus();

            }

        });

    });

    // =====================================================
    // GOOGLE STYLE PRODUCT SEARCH
    // =====================================================

    const deviceSearch =
        document.getElementById("deviceSearch");

    const searchResults =
        document.getElementById("deviceSearchResults");

    const selectedProduct =
        document.getElementById("selectedProductId");

    const variantSelect =
        document.getElementById("variantSelect");

    if (deviceSearch) {

        deviceSearch.addEventListener("keyup", async function () {

            const keyword = this.value.trim();

            if (keyword.length < 2) {

                searchResults.style.display = "none";
                searchResults.innerHTML = "";

                return;

            }

            try {

                const response = await fetch(
                    `/trade-ins/api/search-products?q=${encodeURIComponent(keyword)}`
                );

                const products = await response.json();

                searchResults.innerHTML = "";

                if (!products.length) {

                    searchResults.innerHTML =
                        `<div class="list-group-item">
                            No products found
                        </div>`;

                    searchResults.style.display = "block";

                    return;

                }

                products.forEach(product => {

                    const item =
                        document.createElement("a");

                    item.href = "#";

                    item.className =
                        "list-group-item list-group-item-action";

                    item.innerHTML =
                        `<strong>${product.name}</strong>`;

                    item.onclick = function (e) {

                        e.preventDefault();

                        deviceSearch.value =
                            product.name;

                        selectedProduct.value =
                            product.id;

                        searchResults.style.display =
                            "none";

                        loadVariants(product.id);

                    };

                    searchResults.appendChild(item);

                });

                searchResults.style.display = "block";

            }

            catch (err) {

                console.error(err);

            }

        });

    }

    // =====================================================
    // LOAD VARIANTS
    // =====================================================

    async function loadVariants(productId) {

        if (!variantSelect)
            return;

        variantSelect.innerHTML =
            `<option>Loading...</option>`;

        try {

            const response = await fetch(
                `/trade-ins/api/product/${productId}/variants`
            );

            const variants =
                await response.json();

            variantSelect.innerHTML =
                `<option value="">Select Variant</option>`;

            variants.forEach(v => {

                variantSelect.innerHTML += `
                    <option
                        value="${v.id}"
                        data-brand="${v.brand}"
                        data-model="${v.model}"
                        data-storage="${v.storage}"
                        data-ram="${v.ram}"
                        data-colour="${v.colour}">
                        ${v.storage} / ${v.ram} / ${v.colour}
                    </option>`;

            });

        }

        catch (err) {

            console.error(err);

        }

    }

    // =====================================================
    // DEVICE SUMMARY CARD
    // =====================================================

    variantSelect?.addEventListener("change", function () {

        const option =
            this.selectedOptions[0];

        if (!option || !option.value)
            return;

        document.getElementById(
            "deviceSummaryCard"
        ).style.display = "block";

        document.getElementById(
            "summaryBrand"
        ).textContent =
            option.dataset.brand;

        document.getElementById(
            "summaryModel"
        ).textContent =
            option.dataset.model;

        document.getElementById(
            "summaryStorage"
        ).textContent =
            option.dataset.storage;

        document.getElementById(
            "summaryRam"
        ).textContent =
            option.dataset.ram;

        document.getElementById(
            "summaryColour"
        ).textContent =
            option.dataset.colour;

    });

    // =====================================================
    // REVIEW PAGE
    // =====================================================

    function setReview(id, value) {

        const el =
            document.getElementById(id);

        if (el)
            el.textContent =
                value || "-";

    }

    function updateReview() {

        setReview(
            "reviewCustomer",
            document.querySelector(
                '[name="customer_name"]'
            )?.value
        );

        setReview(
            "reviewPhone",
            document.querySelector(
                '[name="phone_number"]'
            )?.value
        );

        setReview(
            "reviewBusiness",
            document.querySelector(
                '[name="business_name"]'
            )?.value
        );

        setReview(
            "reviewDate",
            document.querySelector(
                '[name="trade_in_date"]'
            )?.value
        );

        setReview(
            "reviewIMEI",
            document.querySelector(
                '[name="imei[]"]'
            )?.value
        );

        setReview(
            "reviewBattery",
            battery?.value
                ? battery.value + "%"
                : "-"
        );

        setReview(
            "reviewScreen",
            document.querySelector(
                '[name="screen_condition[]"]'
            )?.value
        );

        setReview(
            "reviewFrame",
            document.querySelector(
                '[name="frame_condition[]"]'
            )?.value
        );

        setReview(
            "reviewCamera",
            document.querySelector(
                '[name="camera_condition[]"]'
            )?.value
        );

        setReview(
            "reviewTradeValue",
            "UGX " +
            (
                parseFloat(tradeValue?.value) || 0
            ).toLocaleString()
        );

        setReview(
            "reviewSelling",
            "UGX " +
            (
                parseFloat(sellingPrice?.value) || 0
            ).toLocaleString()
        );

        setReview(
            "reviewCash",
            "UGX " +
            (
                parseFloat(
                    document.querySelector(
                        '[name="cash_paid"]'
                    )?.value
                ) || 0
            ).toLocaleString()
        );

        setReview(
            "reviewTopup",
            "UGX " +
            (
                parseFloat(customerTopup?.value) || 0
            ).toLocaleString()
        );

        setReview(
            "reviewProfit",
            expectedProfit?.value
        );

        const selected =
            variantSelect?.selectedOptions[0];

        if (selected) {

            setReview(
                "reviewDevice",
                `${selected.dataset.brand} ${selected.dataset.model} ${selected.dataset.storage}`
            );

        }

    }

    document
        .querySelectorAll("input,select,textarea")
        .forEach(el => {

            el.addEventListener(
                "input",
                updateReview
            );

            el.addEventListener(
                "change",
                updateReview
            );

        });

    // =====================================================
    // FORM VALIDATION
    // =====================================================

    const form =
        document.getElementById("tradeInForm");

    form?.addEventListener(
        "submit",
        function (e) {

            const customer =
                document.querySelector(
                    '[name="customer_name"]'
                );

            const imei =
                document.querySelector(
                    '[name="imei[]"]'
                );

            if (
                !customer?.value.trim() ||
                !selectedProduct?.value ||
                !imei?.value.trim()
            ) {

                e.preventDefault();

                alert(
                    "Please complete all required fields."
                );

                return;

            }

        }
    );

    updateReview();

});