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

    //showStep(0);

    // =====================================================
    // ELEMENTS
    // =====================================================

    const suggestedTradeValue =
    document.getElementById("suggestedTradeValue");

const agreedTradeValue =
    document.querySelector(".agreedTradeValue");

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

const upgradeRadio =
    document.getElementById("upgradePhone");

const downgradeRadio =
    document.getElementById("downgradePhone");

const cashPaidCustomer =
    document.getElementById("cashPaidCustomer");

const customerTopup =
    document.getElementById("customerTopup");

    // =====================================================
    // BUY / SWAP SWITCHING
    // =====================================================

    function updateTransactionMode() {

    const buyRadio =
        document.getElementById("buyPhone");

    const upgradeRadio =
        document.getElementById("upgradePhone");

    const downgradeRadio =
        document.getElementById("downgradePhone");

    const cashPaid =
        document.getElementById("cashPaidCustomer");

    const customerTopup =
        document.getElementById("customerTopup");

    if (
        !buyRadio ||
        !upgradeRadio ||
        !downgradeRadio
    ) {
        return;
    }

    if (buyRadio.checked) {

        cashPaid.parentElement.style.display =
            "block";

        customerTopup.parentElement.style.display =
            "none";

    }

    else if (upgradeRadio.checked) {

        cashPaid.parentElement.style.display =
            "none";

        customerTopup.parentElement.style.display =
            "block";

    }

    else if (downgradeRadio.checked) {

        cashPaid.parentElement.style.display =
            "block";

        customerTopup.parentElement.style.display =
            "none";

    }

    calculateSettlement();

}

document
    .querySelectorAll(
        'input[name="transaction_type"]'
    )
    .forEach(radio => {

        radio.addEventListener(
            "change",
            updateTransactionMode
        );

    });

updateTransactionMode();

    // =====================================================
    // PROFIT
    // =====================================================

    function calculateProfit() {

    const suggestedTradeValue =
        document.getElementById("suggestedTradeValue");

    const agreedTradeValue =
        document.querySelector(".agreedTradeValue");

    const sellingPrice =
        document.querySelector(".sellingPrice");

    const expectedProfit =
        document.getElementById("expectedProfit");

    if (!agreedTradeValue || !sellingPrice)
        return;

    const suggested =
        parseFloat(suggestedTradeValue?.value) || 0;

    const agreed =
        parseFloat(agreedTradeValue.value) || 0;

    const selling =
        parseFloat(sellingPrice.value) || 0;

    const profit =
        selling - agreed;

    if (expectedProfit) {

        expectedProfit.textContent =
            "UGX " +
            profit.toLocaleString();

    }

    document.getElementById("summarySuggested").textContent =
        "UGX " + suggested.toLocaleString();

    document.getElementById("summaryAgreed").textContent =
        "UGX " + agreed.toLocaleString();

    document.getElementById("summarySelling").textContent =
        "UGX " + selling.toLocaleString();

}

    suggestedTradeValue?.addEventListener(
    "input",
    () => {

        calculateProfit();

        updateReview();

    }
);

agreedTradeValue?.addEventListener(
    "input",
    () => {

        calculateProfit();

        calculateSettlement();

        updateReview();

    }
);

sellingPrice?.addEventListener(
    "input",
    () => {

        calculateProfit();

        calculateSettlement();

        updateReview();

    }
);

    // =====================================================
// SMART TRADE VALUATION
// =====================================================

async function calculateSuggestedValue() {

    const suggestedTradeValue =
        document.getElementById("suggestedTradeValue");

    const agreedTradeValue =
        document.querySelector(".agreedTradeValue");

    if (!sellingPrice)
        return;

    try {

        const response = await fetch(
            "/trade-ins/api/valuation",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({

                    selling_price:
                        parseFloat(sellingPrice.value) || 0,

                    battery_health:
                        battery?.value || null,

                    screen_condition:
                        document.querySelector('[name="screen_condition[]"]')?.value,

                    back_condition:
                        document.querySelector('[name="back_condition[]"]')?.value,

                    frame_condition:
                        document.querySelector('[name="frame_condition[]"]')?.value,

                    camera_condition:
                        document.querySelector('[name="camera_condition[]"]')?.value,

                    face_id_status:
                        document.querySelector('[name="face_id_status[]"]')?.value,

                    fingerprint_status:
                        document.querySelector('[name="fingerprint_status[]"]')?.value,

                    network_lock:
                        document.querySelector('[name="network_lock[]"]')?.value,

                    icloud_status:
                        document.querySelector('[name="icloud_status[]"]')?.value,

                    frp_status:
                        document.querySelector('[name="frp_status[]"]')?.value,

                    charger_received:
                        document.querySelector('[name="charger_received[]"]')?.checked,

                    box_received:
                        document.querySelector('[name="box_received[]"]')?.checked

                })

            }
        );

        const result =
            await response.json();

        // ERP Recommendation

        suggestedTradeValue.value =
            result.suggested_trade_value;

        // Only set Agreed Value automatically
        // the first time.

        if (
            agreedTradeValue &&
            !agreedTradeValue.value
        ) {

            agreedTradeValue.value =
                result.suggested_trade_value;

        }

        calculateProfit();

calculateSettlement();

updateReview();
    }

    catch (err) {

        console.error(err);

    }

}

    // =====================================================
    // TOP-UP CALCULATION
    // =====================================================

    function calculateSettlement() {

    const agreedTradeValue =
        document.querySelector(".agreedTradeValue");

    const cashPaid =
        document.getElementById("cashPaidCustomer");

    const customerTopup =
        document.getElementById("customerTopup");

    const buyRadio =
        document.getElementById("buyPhone");

    const upgradeRadio =
        document.getElementById("upgradePhone");

    const downgradeRadio =
        document.getElementById("downgradePhone");

    const agreed =
        parseFloat(
            agreedTradeValue?.value
        ) || 0;

    const selling =
        parseFloat(
            sellingPrice?.value
        ) || 0;

    // BUY
    if (buyRadio?.checked) {

        cashPaid.value = agreed;

        customerTopup.value = 0;

    }

    // UPGRADE
    else if (upgradeRadio?.checked) {

        const topup =
            Math.max(
                selling - agreed,
                0
            );

        customerTopup.value = topup;

        cashPaid.value = 0;

    }

    // DOWNGRADE
    else if (downgradeRadio?.checked) {

        const refund =
            Math.max(
                agreed - selling,
                0
            );

        cashPaid.value = refund;

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

                        const item = document.createElement("a");

                        item.href = "#";

                        item.className =
                            "list-group-item list-group-item-action p-3";

                        item.innerHTML = `

                            <div class="d-flex justify-content-between align-items-center">

                               <div>

                                   <h6 class="mb-1 fw-bold">

                                        <i class="fas fa-mobile-alt text-success me-2"></i>

                                        ${product.name}

                                    </h6>

                                    <small class="text-muted">

                                        Click to load available variants

                                    </small>

                                </div>

                                <i class="fas fa-chevron-right text-secondary"></i>

                            </div>

                        `;

                        item.onclick = function(e){

                            e.preventDefault();

                            deviceSearch.value = product.name;

                            selectedProduct.value = product.id;

                            searchResults.style.display = "none";

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
            data-colour="${v.colour}"
            data-condition="${v.condition}"
            data-stock="${v.stock}"
            data-price="${v.selling_price}"
            data-sku="${v.sku}">

            ${v.storage} • ${v.ram} RAM • ${v.colour}

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

    const option = this.selectedOptions[0];

    if (!option || !option.value)
        return;

    document.getElementById("deviceSummaryCard").style.display = "block";

    document.getElementById("summaryBrand").textContent =
        option.dataset.brand;

    document.getElementById("summaryModel").textContent =
        option.dataset.model;

    document.getElementById("summaryStorage").textContent =
        option.dataset.storage;

    document.getElementById("summaryRam").textContent =
        option.dataset.ram;

    document.getElementById("summaryColour").textContent =
        option.dataset.colour;

    document.getElementById("summarySku").textContent =
        option.dataset.sku;

    document.getElementById("summaryCondition").textContent =
        option.dataset.condition;

    document.getElementById("summaryStock").textContent =
        option.dataset.stock + " Units";

    document.getElementById("summarySellingPrice").textContent =
        "UGX " +
        Number(option.dataset.price).toLocaleString();

    if (sellingPrice) {

        sellingPrice.value = option.dataset.price;

    }

    calculateProfit();

calculateSettlement();

calculateSuggestedValue();

updateReview();

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
        parseFloat(agreedTradeValue?.value) || 0
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

        const agreed =
    parseFloat(agreedTradeValue?.value) || 0;

const selling =
    parseFloat(sellingPrice?.value) || 0;

setReview(
    "reviewProfit",
    "UGX " +
    (selling - agreed).toLocaleString()
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
                () => {

                updateReview();

                calculateSuggestedValue();

                }
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

    showStep(0);

});