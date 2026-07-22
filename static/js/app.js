document.addEventListener("DOMContentLoaded", () => {

    const addBtn = document.getElementById("addRow");
    const tbody = document.getElementById("purchaseBody");
    const template = document.getElementById("purchaseRowTemplate");
    const grandTotal = document.getElementById("grandTotal");

    if (!addBtn || !tbody || !template) return;

    function updateTotals() {

        let total = 0;

        tbody.querySelectorAll("tr").forEach(row => {

            const qty = parseFloat(row.querySelector(".qty").value) || 0;
            const cost = parseFloat(row.querySelector(".cost").value) || 0;

            const subtotal = qty * cost;

            row.querySelector(".subtotal").value =
                subtotal.toLocaleString();

            total += subtotal;

        });

        grandTotal.textContent = total.toLocaleString();

    }

    addBtn.addEventListener("click", () => {

        const clone = template.content.cloneNode(true);

        tbody.appendChild(clone);

        updateTotals();

    });

    tbody.addEventListener("input", e => {

        if (
            e.target.classList.contains("qty") ||
            e.target.classList.contains("cost")
        ) {
            updateTotals();
        }

    });

    tbody.addEventListener("click", e => {

        const btn = e.target.closest(".removeRow");

        if (!btn) return;

        if (tbody.querySelectorAll("tr").length > 1) {

            btn.closest("tr").remove();

            updateTotals();

        }

    });

    updateTotals();

});