document.addEventListener("DOMContentLoaded", () => {

    const container =
        document.getElementById("purchaseItemsContainer");

    const addButton =
        document.getElementById("addItem");

    const template =
        document.getElementById("purchaseItemTemplate");

    const grandCost =
        document.getElementById("grandCost");

    const grandSales =
        document.getElementById("grandSales");

    const grandProfit =
        document.getElementById("grandProfit");



    //----------------------------------------------------
    // Currency
    //----------------------------------------------------

    function money(value) {

        return Number(value || 0).toLocaleString();

    }



    //----------------------------------------------------
    // Count IMEIs
    //----------------------------------------------------

    function imeiCount(card) {

        const textarea =
            card.querySelector(".imeiList");

        if (!textarea)
            return 0;

        return textarea.value
            .split("\n")
            .map(i => i.trim())
            .filter(i => i !== "")
            .length;

    }



    //----------------------------------------------------
    // Update single card
    //----------------------------------------------------

    function updateCard(card) {

        const qty =
            Number(
                card.querySelector(".quantity").value || 0
            );

        const buying =
            Number(
                card.querySelector(".buyingPrice").value || 0
            );

        const selling =
            Number(
                card.querySelector(".sellingPrice").value || 0
            );

        const imeis =
            imeiCount(card);

        card.querySelector(".imeiCount").innerText =
            imeis;

        card.querySelector(".requiredCount").innerText =
            qty;

        card.querySelector(".inventoryCost").innerText =
            "UGX " + money(
                qty * buying
            );

        card.querySelector(".expectedSales").innerText =
            "UGX " + money(
                qty * selling
            );

        const validation =
            card.querySelector(".validationBox");

        validation.classList.add("d-none");

        validation.innerHTML = "";

        if (imeis !== qty) {

            validation.classList.remove("d-none");

            validation.innerHTML =
                "<strong>IMEI count must equal Quantity.</strong>";

        }

        updateGrandTotals();

    }



    //----------------------------------------------------
    // Grand Totals
    //----------------------------------------------------

    function updateGrandTotals() {

        let totalCost = 0;

        let totalSales = 0;

        document
            .querySelectorAll(".purchase-item")
            .forEach(card => {

                const qty =
                    Number(
                        card.querySelector(".quantity").value || 0
                    );

                const buying =
                    Number(
                        card.querySelector(".buyingPrice").value || 0
                    );

                const selling =
                    Number(
                        card.querySelector(".sellingPrice").value || 0
                    );

                totalCost += qty * buying;

                totalSales += qty * selling;

            });

        grandCost.innerText =
            money(totalCost);

        grandSales.innerText =
            money(totalSales);

        grandProfit.innerText =
            money(totalSales - totalCost);

    }
        //----------------------------------------------------
    // Attach Events
    //----------------------------------------------------

    function attachEvents(card) {

        card.querySelector(".quantity")
            .addEventListener("input", () => {
                updateCard(card);
            });

        card.querySelector(".buyingPrice")
            .addEventListener("input", () => {
                updateCard(card);
            });

        card.querySelector(".sellingPrice")
            .addEventListener("input", () => {
                updateCard(card);
            });

        card.querySelector(".imeiList")
            .addEventListener("input", () => {
                updateCard(card);
            });

        card.querySelector(".removeItem")
            .addEventListener("click", () => {

                if (
                    document.querySelectorAll(".purchase-item").length === 1
                ) {

                    alert(
                        "At least one purchase item is required."
                    );

                    return;

                }

                card.remove();

                updateGrandTotals();

            });

    }



    //----------------------------------------------------
    // Duplicate IMEI Check
    //----------------------------------------------------

    function duplicateIMEIs() {

        let seen = [];

        let duplicates = [];

        document
            .querySelectorAll(".imeiList")
            .forEach(box => {

                box.value
                    .split("\n")
                    .map(i => i.trim())
                    .filter(i => i !== "")
                    .forEach(i => {

                        if (seen.includes(i)) {

                            duplicates.push(i);

                        }

                        else {

                            seen.push(i);

                        }

                    });

            });

        return duplicates;

    }



    //----------------------------------------------------
    // Validate Form
    //----------------------------------------------------

    function validatePurchase() {

        let valid = true;

        document
            .querySelectorAll(".purchase-item")
            .forEach(card => {

                updateCard(card);

                const qty =
                    Number(
                        card.querySelector(".quantity").value || 0
                    );

                const imeis =
                    imeiCount(card);

                if (qty !== imeis) {

                    valid = false;

                }

            });

        const dup = duplicateIMEIs();

        if (dup.length > 0) {

            alert(
                "Duplicate IMEIs found:\n\n" +
                dup.join("\n")
            );

            return false;

        }

        if (!valid) {

            alert(
                "Some purchase items have incorrect IMEI counts."
            );

            return false;

        }

        return true;

    }



    //----------------------------------------------------
    // Add Item
    //----------------------------------------------------

    addButton.addEventListener("click", () => {

        const clone =
            template.content.cloneNode(true);

        container.appendChild(clone);

        const cards =
            document.querySelectorAll(".purchase-item");

        const newCard =
            cards[cards.length - 1];

        attachEvents(newCard);

        updateCard(newCard);

    });
        //----------------------------------------------------
    // Initialise Existing Card
    //----------------------------------------------------

    document
        .querySelectorAll(".purchase-item")
        .forEach(card => {

            attachEvents(card);

            updateCard(card);

        });



    //----------------------------------------------------
    // Form Submit Validation
    //----------------------------------------------------

    const purchaseForm =
        document.getElementById("purchaseForm");

    purchaseForm.addEventListener(
        "submit",
        function (e) {

            if (!validatePurchase()) {

                e.preventDefault();

                return;

            }

        }
    );



    //----------------------------------------------------
    // Barcode Scanner Mode
    // (Preparation for Scanner Integration)
    //----------------------------------------------------

    document
        .querySelectorAll(".imeiMode")
        .forEach(select => {

            select.addEventListener(
                "change",
                function () {

                    const card =
                        this.closest(".purchase-item");

                    const textarea =
                        card.querySelector(".imeiList");

                    if (this.value === "scanner") {

                        textarea.placeholder =
                            "Scan each barcode one after another...";

                        textarea.focus();

                    }

                    else if (this.value === "paste") {

                        textarea.placeholder =
                            "Paste one IMEI per line...";

                    }

                    else {

                        textarea.placeholder =
                            "Enter one IMEI per line";

                    }

                }
            );

        });



    //----------------------------------------------------
    // Future Features
    //----------------------------------------------------
    //
    // ✔ Live barcode scanner (USB)
    // ✔ Camera barcode scanner
    // ✔ Import CSV IMEIs
    // ✔ Duplicate IMEI check against database
    // ✔ Auto-fill variant from scanned IMEI
    // ✔ Draft purchase saving
    // ✔ Resume draft purchase
    // ✔ Supplier catalogue integration
    //
    //----------------------------------------------------

});