// ===============================
// Shopping Cart
// ===============================

let cart = [];

// -------------------------------
// Add Item
// -------------------------------
function addToCart(item) {

    if (item.imei_id) {

        const exists = cart.find(i => i.imei_id == item.imei_id);

        if (exists) {
            alert("This IMEI is already in the cart.");
            return;
        }

    }

    cart.push(item);

    renderCart();
}

// -------------------------------
// Remove Item
// -------------------------------
function removeCartItem(index) {

    cart.splice(index, 1);

    renderCart();

}

// -------------------------------
// Render Cart
// -------------------------------
function renderCart() {

    const cartBody = document.getElementById("cartBody");

    const itemCount = document.getElementById("itemCount");

    const grandTotal = document.getElementById("grandTotal");

    const completeSaleBtn = document.getElementById("completeSaleBtn");

    cartBody.innerHTML = "";

    if (cart.length === 0) {

        cartBody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center text-muted">
                    No items added yet
                </td>
            </tr>
        `;

        itemCount.textContent = "0";

        grandTotal.textContent = "UGX 0";

        completeSaleBtn.disabled = true;

        return;
    }

    let total = 0;

    cart.forEach((item, index) => {

        total += item.total;

        cartBody.innerHTML += `
            <tr>

                <td>${item.product}</td>

                <td>${item.imei}</td>

                <td>${item.quantity}</td>

                <td>${item.price.toLocaleString()}</td>

                <td>${item.total.toLocaleString()}</td>

                <td>

                    <button
                        class="btn btn-sm btn-danger"
                        onclick="removeCartItem(${index})">

                        <i class="fas fa-trash"></i>

                    </button>

                </td>

            </tr>
        `;

    });

        itemCount.textContent = cart.length;

    grandTotal.textContent = "UGX " + total.toLocaleString();

    completeSaleBtn.disabled = false;

    // Store the entire cart in the hidden input
    const cartInput = document.getElementById("cartItems");

    if (cartInput) {
        cartInput.value = JSON.stringify(cart);
    }

}