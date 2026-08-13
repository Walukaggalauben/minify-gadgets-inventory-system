document.addEventListener("DOMContentLoaded", () => {

    // ============================================================
    // TRADE-IN WIZARD
    // PART 1 — CORE WIZARD + TRADE MODE + PROFIT
    // ============================================================

    const steps = document.querySelectorAll(".wizard-step");
    const navLinks = document.querySelectorAll("#tradeWizard .nav-link");

    let currentStep = 0;


    // ============================================================
    // WIZARD NAVIGATION
    // ============================================================

    function showStep(index) {

        if (!steps.length) {
            return;
        }

        if (index < 0) {
            index = 0;
        }

        if (index >= steps.length) {
            index = steps.length - 1;
        }

        steps.forEach((step, i) => {

            step.classList.toggle(
                "active-step",
                i === index
            );

            step.classList.toggle(
                "d-none",
                i !== index
            );

        });


        navLinks.forEach((nav, i) => {

            nav.classList.toggle(
                "active",
                i === index
            );

        });


        currentStep = index;

        updateReview();

    }


    // ============================================================
    // NEXT BUTTONS
    // ============================================================

    document.querySelectorAll(".nextStep").forEach(button => {

        button.addEventListener("click", () => {

            if (currentStep < steps.length - 1) {

                showStep(currentStep + 1);

            }

        });

    });


    // ============================================================
    // PREVIOUS BUTTONS
    // ============================================================

    document.querySelectorAll(".prevStep").forEach(button => {

        button.addEventListener("click", () => {

            if (currentStep > 0) {

                showStep(currentStep - 1);

            }

        });

    });


    // ============================================================
    // MAIN ELEMENTS
    // ============================================================

    const tradeValue =
        document.querySelector(".finalTradeValue");

    const sellingPrice =
        document.querySelector(".sellingPrice");

    const expectedProfit =
        document.getElementById("expectedProfit");

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


    // ============================================================
    // HELPERS
    // ============================================================

    function getFirstField(name) {

        return document.querySelector(
            `[name="${name}"]`
        );

    }


    function getFirstValue(name) {

        return getFirstField(name)?.value || "";

    }


    function getFirstChecked(name) {

        return Boolean(
            getFirstField(name)?.checked
        );

    }


    function money(value) {

        const number =
            Number(value) || 0;

        return (
            "UGX " +
            number.toLocaleString()
        );

    }


    // ============================================================
    // BUY / SWAP MODE
    // ============================================================

    function updateTradeMode() {

        if (!buyRadio || !swapRadio) {
            return;
        }


        if (buyRadio.checked) {

            if (buySection) {
                buySection.style.display = "block";
            }

            if (swapSection) {
                swapSection.style.display = "none";
            }

        }


        if (swapRadio.checked) {

            if (buySection) {
                buySection.style.display = "none";
            }

            if (swapSection) {
                swapSection.style.display = "block";
            }

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


    // ============================================================
    // PROFIT CALCULATION
    // ============================================================

    function calculateProfit() {

        if (!tradeValue || !expectedProfit) {
            return;
        }


        let selling = 0;


        if (buyRadio?.checked) {

            selling =
                parseFloat(
                    sellingPrice?.value
                ) || 0;

        }


        if (swapRadio?.checked) {

            selling =
                parseFloat(
                    swapSellingPrice?.value
                ) || 0;

        }


        const buying =
            parseFloat(
                tradeValue.value
            ) || 0;


        const profit =
            selling - buying;


        expectedProfit.value =
            money(profit);


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


    // ============================================================
    // TOP-UP CALCULATION
    // ============================================================

    function calculateTopup() {

        if (!swapRadio?.checked) {
            return;
        }


        const selling =
            parseFloat(
                swapSellingPrice?.value
            ) || 0;


        const trade =
            parseFloat(
                tradeValue?.value
            ) || 0;


        const difference =
            selling - trade;


        if (customerTopup) {

            customerTopup.value =
                difference > 0
                    ? difference
                    : 0;

        }

    }


    // ============================================================
    // INITIAL TRADE MODE
    // ============================================================

    updateTradeMode();
    // ============================================================
// TRADE-IN WIZARD
// PART 2 — CUSTOMER + DEVICE SEARCH
// ============================================================


// ============================================================
// CUSTOMER SEARCH
// ============================================================

const customerSearch =
    document.getElementById("customerSearch");

const customerResults =
    document.getElementById("customerResults");

const selectedCustomerCard =
    document.getElementById("selectedCustomerCard");

const selectedCustomerName =
    document.getElementById("selectedCustomerName");

const selectedCustomerPhone =
    document.getElementById("selectedCustomerPhone");


// Store selected customer

let selectedCustomer = null;


// ------------------------------------------------------------
// SEARCH CUSTOMERS
// ------------------------------------------------------------

customerSearch?.addEventListener(
    "input",
    async function () {

        const keyword =
            this.value.trim();

        if (keyword.length < 2) {

            if (customerResults) {

                customerResults.style.display =
                    "none";

                customerResults.innerHTML =
                    "";

            }

            return;
        }


        try {

            const response =
                await fetch(
                    `/customers/api/search?q=${encodeURIComponent(keyword)}`
                );


            if (!response.ok) {

                throw new Error(
                    "Customer search failed"
                );

            }


            const customers =
                await response.json();


            if (!customerResults) {
                return;
            }


            customerResults.innerHTML =
                "";


            if (!customers.length) {

                customerResults.innerHTML = `
                    <div class="list-group-item text-muted">
                        <i class="fas fa-user-slash me-2"></i>
                        No customer found
                    </div>
                `;

                customerResults.style.display =
                    "block";

                return;
            }


            customers.forEach(customer => {

                const item =
                    document.createElement("button");

                item.type =
                    "button";

                item.className =
                    "list-group-item list-group-item-action";


                item.innerHTML = `
                    <div class="d-flex justify-content-between align-items-center">

                        <div>

                            <strong>
                                ${customer.name || ""}
                            </strong>

                            <br>

                            <small class="text-muted">

                                <i class="fas fa-phone me-1"></i>

                                ${customer.phone || "No phone"}

                            </small>

                        </div>

                        <span class="badge bg-success">

                            ${customer.code || ""}

                        </span>

                    </div>
                `;


                item.addEventListener(
                    "click",
                    function () {

                        selectCustomer(
                            customer
                        );

                    }
                );


                customerResults.appendChild(
                    item
                );

            });


            customerResults.style.display =
                "block";

        }

        catch (error) {

            console.error(
                "Customer search error:",
                error
            );

        }

    }
);


// ------------------------------------------------------------
// SELECT CUSTOMER
// ------------------------------------------------------------

function selectCustomer(customer) {

    selectedCustomer =
        customer;


    if (customerSearch) {

        customerSearch.value =
            customer.name || "";

    }


    if (customerResults) {

        customerResults.style.display =
            "none";

        customerResults.innerHTML =
            "";

    }


    if (selectedCustomerCard) {

        selectedCustomerCard.style.display =
            "block";

    }


    if (selectedCustomerName) {

        selectedCustomerName.textContent =
            customer.name || "";

    }


    if (selectedCustomerPhone) {

        selectedCustomerPhone.textContent =
            customer.phone || "";

    }


    // --------------------------------------------------------
    // AUTO-FILL CUSTOMER DETAILS
    // --------------------------------------------------------

    setFieldValue(
        "customer_name",
        customer.name
    );

    setFieldValue(
        "phone_number",
        customer.phone
    );

    setFieldValue(
        "alternative_phone",
        customer.alternative_phone
    );

    setFieldValue(
        "email",
        customer.email
    );

    setFieldValue(
        "national_id",
        customer.national_id
    );

    setFieldValue(
        "address",
        customer.address
    );

    setFieldValue(
        "business_name",
        customer.business_name
    );

}


// ============================================================
// SET FORM FIELD
// ============================================================

function setFieldValue(
    name,
    value
) {

    const field =
        document.querySelector(
            `[name="${name}"]`
        );


    if (field) {

        field.value =
            value || "";

    }

}


// ============================================================
// CLEAR CUSTOMER
// ============================================================

function clearSelectedCustomer() {

    selectedCustomer =
        null;


    if (selectedCustomerCard) {

        selectedCustomerCard.style.display =
            "none";

    }


    if (customerSearch) {

        customerSearch.value =
            "";

    }

}


// ============================================================
// DEVICE SEARCH
// ============================================================

const deviceSearch =
    document.getElementById(
        "deviceSearch"
    );

const deviceSearchResults =
    document.getElementById(
        "deviceSearchResults"
    );

const selectedProductId =
    document.getElementById(
        "selectedProductId"
    );

const variantSelect =
    document.getElementById(
        "variantSelect"
    );


// ------------------------------------------------------------
// SEARCH PRODUCTS
// ------------------------------------------------------------

deviceSearch?.addEventListener(
    "input",
    async function () {

        const keyword =
            this.value.trim();


        if (keyword.length < 2) {

            if (deviceSearchResults) {

                deviceSearchResults.style.display =
                    "none";

                deviceSearchResults.innerHTML =
                    "";

            }

            return;
        }


        try {

            const response =
                await fetch(
                    `/trade-ins/api/search-products?q=${encodeURIComponent(keyword)}`
                );


            if (!response.ok) {

                throw new Error(
                    "Product search failed"
                );

            }


            const products =
                await response.json();


            if (!deviceSearchResults) {
                return;
            }


            deviceSearchResults.innerHTML =
                "";


            if (!products.length) {

                deviceSearchResults.innerHTML = `
                    <div class="list-group-item text-muted">
                        <i class="fas fa-search me-2"></i>
                        No devices found
                    </div>
                `;

                deviceSearchResults.style.display =
                    "block";

                return;
            }


            products.forEach(product => {

                const item =
                    document.createElement("button");

                item.type =
                    "button";

                item.className =
                    "list-group-item list-group-item-action";


                item.innerHTML = `
                    <i class="fas fa-mobile-screen-button me-2 text-success"></i>

                    <strong>
                        ${product.name || ""}
                    </strong>
                `;


                item.addEventListener(
                    "click",
                    function () {

                        deviceSearch.value =
                            product.name || "";

                        selectedProductId.value =
                            product.id;


                        deviceSearchResults.style.display =
                            "none";

                        deviceSearchResults.innerHTML =
                            "";


                        loadVariants(
                            product.id
                        );

                    }
                );


                deviceSearchResults.appendChild(
                    item
                );

            });


            deviceSearchResults.style.display =
                "block";

        }

        catch (error) {

            console.error(
                "Device search error:",
                error
            );

        }

    }
);


// ============================================================
// LOAD PRODUCT VARIANTS
// ============================================================

async function loadVariants(
    productId
) {

    if (!variantSelect) {
        return;
    }


    variantSelect.innerHTML = `
        <option value="">
            Loading variants...
        </option>
    `;


    try {

        const response =
            await fetch(
                `/trade-ins/api/product/${productId}/variants`
            );


        if (!response.ok) {

            throw new Error(
                "Variant request failed"
            );

        }


        const variants =
            await response.json();


        variantSelect.innerHTML = `
            <option value="">
                Select Variant
            </option>
        `;


        variants.forEach(
            variant => {

                variantSelect.innerHTML += `
                    <option
                        value="${variant.id}"
                        data-brand="${variant.brand || ""}"
                        data-model="${variant.model || ""}"
                        data-storage="${variant.storage || ""}"
                        data-ram="${variant.ram || ""}"
                        data-colour="${variant.colour || ""}"
                        data-sku="${variant.sku || ""}"
                        data-stock="${variant.stock || 0}"
                        data-condition="${variant.condition || ""}"
                        data-price="${variant.selling_price || 0}"
                    >

                        ${variant.storage || ""}
                        /
                        ${variant.ram || ""}
                        /
                        ${variant.colour || ""}

                    </option>
                `;

            }
        );

    }

    catch (error) {

        console.error(
            "Variant loading error:",
            error
        );


        variantSelect.innerHTML = `
            <option value="">
                Unable to load variants
            </option>
        `;

    }

}


// ============================================================
// DEVICE SUMMARY
// ============================================================

variantSelect?.addEventListener(
    "change",
    function () {

        const option =
            this.selectedOptions[0];


        if (
            !option ||
            !option.value
        ) {

            return;

        }


        const summaryCard =
            document.getElementById(
                "deviceSummaryCard"
            );


        if (summaryCard) {

            summaryCard.style.display =
                "block";

        }


        setText(
            "summaryBrand",
            option.dataset.brand
        );

        setText(
            "summaryModel",
            option.dataset.model
        );

        setText(
            "summaryStorage",
            option.dataset.storage
        );

        setText(
            "summaryRam",
            option.dataset.ram
        );

        setText(
            "summaryColour",
            option.dataset.colour
        );

        setText(
            "summarySku",
            option.dataset.sku
        );

        setText(
            "summaryCondition",
            option.dataset.condition
        );

        setText(
            "summaryStock",
            option.dataset.stock
        );

        setText(
            "summarySellingPrice",
            money(
                option.dataset.price
            )
        );

    }
);


// ============================================================
// SET TEXT HELPER
// ============================================================

function setText(
    id,
    value
) {

    const element =
        document.getElementById(id);


    if (element) {

        element.textContent =
            value || "-";

    }

}


// ============================================================
// CLOSE SEARCH DROPDOWNS WHEN CLICKING OUTSIDE
// ============================================================

document.addEventListener(
    "click",
    function (event) {

        if (
            customerResults &&
            customerSearch &&
            !customerSearch.contains(event.target) &&
            !customerResults.contains(event.target)
        ) {

            customerResults.style.display =
                "none";

        }


        if (
            deviceSearchResults &&
            deviceSearch &&
            !deviceSearch.contains(event.target) &&
            !deviceSearchResults.contains(event.target)
        ) {

            deviceSearchResults.style.display =
                "none";

        }

    }
);
