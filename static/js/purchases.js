document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById("purchaseItemsContainer");
    const addButton = document.getElementById("addItem");
    const template = document.getElementById("purchaseItemTemplate");
    const purchaseForm = document.getElementById("purchaseForm");

    const grandCost = document.getElementById("grandCost");
    const grandSales = document.getElementById("grandSales");
    const grandProfit = document.getElementById("grandProfit");

    if (!container || !addButton || !template || !purchaseForm) return;

    function number(value) {
        const n = Number(value);
        return Number.isFinite(n) ? n : 0;
    }

    function money(value) {
        return Math.round(number(value)).toLocaleString("en-US");
    }

    function getImeis(card) {
        const textarea = card.querySelector(".imeiList");
        if (!textarea) return [];

        return textarea.value
            .split(/\r?\n/)
            .map(value => value.trim())
            .filter(Boolean);
    }

    function updateItemNumbers() {
        container.querySelectorAll(".purchase-item").forEach((card, index) => {
            const numberEl = card.querySelector(".item-number");
            if (numberEl) numberEl.textContent = String(index + 1).padStart(2, "0");
        });
    }

    function updateVariantOptions(card, searchValue = "") {
        const select = card.querySelector(".variant");
        if (!select) return;

        const term = searchValue.trim().toLowerCase();

        Array.from(select.options).forEach(option => {
            if (!option.value) {
                option.hidden = false;
                return;
            }

            option.hidden = term !== "" &&
                !option.textContent.toLowerCase().includes(term);
        });

        // If the currently selected option was filtered out, clear it.
        if (select.selectedOptions[0]?.hidden) {
            select.value = "";
        }
    }

    function loadVariantPrices(card) {
        const select = card.querySelector(".variant");
        const selected = select?.selectedOptions?.[0];

        if (!selected || !selected.value) return;

        const buying = number(selected.dataset.buying);
        const selling = number(selected.dataset.selling);

        const buyingInput = card.querySelector(".buyingPrice");
        const sellingInput = card.querySelector(".sellingPrice");

        if (buyingInput) buyingInput.value = buying;
        if (sellingInput) sellingInput.value = selling;
    }

    function updateCard(card) {
        const qtyInput = card.querySelector(".quantity");
        const buyingInput = card.querySelector(".buyingPrice");
        const sellingInput = card.querySelector(".sellingPrice");

        const qty = Math.max(0, Math.floor(number(qtyInput?.value)));
        const buying = Math.max(0, number(buyingInput?.value));
        const selling = Math.max(0, number(sellingInput?.value));
        const imeis = getImeis(card);

        if (qtyInput && qty < 1) qtyInput.value = 1;

        const imeiCount = card.querySelector(".imeiCount");
        const requiredCount = card.querySelector(".requiredCount");
        const inventoryCost = card.querySelector(".inventoryCost");
        const expectedSales = card.querySelector(".expectedSales");
        const validation = card.querySelector(".validationBox");

        if (imeiCount) imeiCount.textContent = imeis.length.toLocaleString();
        if (requiredCount) requiredCount.textContent = qty.toLocaleString();
        if (inventoryCost) inventoryCost.textContent = `UGX ${money(qty * buying)}`;
        if (expectedSales) expectedSales.textContent = `UGX ${money(qty * selling)}`;

        if (validation) {
            validation.classList.add("d-none");
            validation.innerHTML = "";
        }

        // Empty IMEIs are allowed for non-IMEI stock.
        // Once an IMEI is started, require one per unit.
        if (imeis.length > 0 && imeis.length !== qty && validation) {
            validation.classList.remove("d-none");
            validation.innerHTML =
                `<i class="fas fa-triangle-exclamation me-1"></i>
                 This item has ${imeis.length} IMEI(s), but the quantity is ${qty}.
                 Enter one IMEI for every unit or clear the IMEI field for non-IMEI stock.`;
        }

        updateGrandTotals();
    }

    function updateGrandTotals() {
        let totalCost = 0;
        let totalSales = 0;

        container.querySelectorAll(".purchase-item").forEach(card => {
            const qty = Math.max(0, Math.floor(number(card.querySelector(".quantity")?.value)));
            const buying = Math.max(0, number(card.querySelector(".buyingPrice")?.value));
            const selling = Math.max(0, number(card.querySelector(".sellingPrice")?.value));

            totalCost += qty * buying;
            totalSales += qty * selling;
        });

        grandCost.textContent = money(totalCost);
        grandSales.textContent = money(totalSales);
        grandProfit.textContent = money(totalSales - totalCost);
    }

    function showValidation(card, message) {
        const box = card.querySelector(".validationBox");
        if (!box) return;

        box.classList.remove("d-none");
        box.innerHTML = `<i class="fas fa-triangle-exclamation me-1"></i>${message}`;
    }

    function attachEvents(card) {
        const quantity = card.querySelector(".quantity");
        const buying = card.querySelector(".buyingPrice");
        const selling = card.querySelector(".sellingPrice");
        const imeiList = card.querySelector(".imeiList");
        const variant = card.querySelector(".variant");
        const variantSearch = card.querySelector(".variantSearch");
        const imeiMode = card.querySelector(".imeiMode");
        const removeButton = card.querySelector(".removeItem");

        quantity?.addEventListener("input", () => updateCard(card));
        buying?.addEventListener("input", () => updateCard(card));
        selling?.addEventListener("input", () => updateCard(card));
        imeiList?.addEventListener("input", () => updateCard(card));

        variant?.addEventListener("change", () => {
            loadVariantPrices(card);
            updateCard(card);
        });

        variantSearch?.addEventListener("input", () => {
            updateVariantOptions(card, variantSearch.value);
        });

        imeiMode?.addEventListener("change", () => {
            if (!imeiList) return;

            if (imeiMode.value === "scanner") {
                imeiList.placeholder = "Scan each IMEI. Most USB scanners will add a new line automatically.";
                imeiList.focus();
            } else if (imeiMode.value === "paste") {
                imeiList.placeholder = "Paste one IMEI per line...";
            } else {
                imeiList.placeholder = "Enter one IMEI per line";
            }
        });

        removeButton?.addEventListener("click", () => {
            const cards = container.querySelectorAll(".purchase-item");

            if (cards.length === 1) {
                alert("At least one purchase item is required.");
                return;
            }

            card.remove();
            updateItemNumbers();
            updateGrandTotals();
        });

        updateVariantOptions(card);
        updateCard(card);
    }

    function findDuplicateImeis() {
        const seen = new Set();
        const duplicates = new Set();

        container.querySelectorAll(".imeiList").forEach(textarea => {
            getImeis(textarea.closest(".purchase-item")).forEach(imei => {
                const normalized = imei.toUpperCase();

                if (seen.has(normalized)) {
                    duplicates.add(imei);
                } else {
                    seen.add(normalized);
                }
            });
        });

        return Array.from(duplicates);
    }

    function validatePurchase() {
        let valid = true;

        const cards = container.querySelectorAll(".purchase-item");

        cards.forEach(card => {
            const variant = card.querySelector(".variant");
            const qty = Math.floor(number(card.querySelector(".quantity")?.value));
            const buying = number(card.querySelector(".buyingPrice")?.value);
            const selling = number(card.querySelector(".sellingPrice")?.value);
            const imeis = getImeis(card);

            updateCard(card);

            if (!variant?.value) {
                valid = false;
                showValidation(card, "Please select a product variant.");
                return;
            }

            if (qty < 1) {
                valid = false;
                showValidation(card, "Quantity must be at least 1.");
                return;
            }

            if (buying < 0 || selling < 0) {
                valid = false;
                showValidation(card, "Prices cannot be negative.");
                return;
            }

            // Empty IMEI list means non-IMEI stock.
            if (imeis.length > 0 && imeis.length !== qty) {
                valid = false;
                showValidation(card, `IMEI count (${imeis.length}) must match quantity (${qty}).`);
            }

            const unique = new Set(imeis.map(i => i.toUpperCase()));
            if (unique.size !== imeis.length) {
                valid = false;
                showValidation(card, "Duplicate IMEIs exist inside this item. Remove duplicates before saving.");
            }
        });

        const duplicates = findDuplicateImeis();

        if (duplicates.length) {
            valid = false;
            alert(
                "Duplicate IMEIs found across purchase items:\n\n" +
                duplicates.join("\n")
            );
        }

        if (!valid) {
            window.scrollTo({ top: container.offsetTop - 90, behavior: "smooth" });
        }

        return valid;
    }

    addButton.addEventListener("click", () => {
        const clone = template.content.cloneNode(true);
        container.appendChild(clone);

        const cards = container.querySelectorAll(".purchase-item");
        const newCard = cards[cards.length - 1];

        attachEvents(newCard);
        updateItemNumbers();

        newCard.scrollIntoView({ behavior: "smooth", block: "center" });
    });

    container.querySelectorAll(".purchase-item").forEach(attachEvents);
    updateItemNumbers();
    updateGrandTotals();

    purchaseForm.addEventListener("submit", event => {
        if (!validatePurchase()) {
            event.preventDefault();
            return;
        }

        const button = document.getElementById("completePurchase");
        if (button) {
            button.disabled = true;
            button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Saving Purchase...';
        }
    });
});

/* Barcode scanner support for receiving purchases */
document.addEventListener("keydown", async (event) => {
    const target = event.target;
    if (!target?.classList?.contains("itemBarcode") || event.key !== "Enter") return;
    event.preventDefault();
    const code = target.value.trim();
    if (!code) return;
    const card = target.closest(".purchase-item");
    try {
        const response = await fetch(`/inventory/api/barcode/${encodeURIComponent(code)}`);
        if (!response.ok) throw new Error("not found");
        const data = await response.json();
        const select = card.querySelector(".variant");
        select.value = String(data.id);
        select.dispatchEvent(new Event("change"));
        target.value = "";
        const note = card.querySelector(".imei-method-note");
        if (note) note.innerHTML = `<i class="fas fa-barcode"></i> Scanned <strong>${data.sku}</strong> — ${data.product}`;
    } catch (_) {
        alert(`No product variant matches barcode "${code}".`);
    }
});
