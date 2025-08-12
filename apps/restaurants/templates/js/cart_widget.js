
    // Function to get CSRF token (uncomment in production)
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');    

    function toggleWidget() {
        const content = document.getElementById('cart-content');
        const icon = document.getElementById('widget-toggle-icon');
        if (content.style.display === 'none' || content.style.display === '') {
            content.style.display = 'block';
            icon.classList.remove('fa-chevron-down');
            icon.classList.add('fa-chevron-up');
        } else {
            content.style.display = 'none';
            icon.classList.remove('fa-chevron-up');
            icon.classList.add('fa-chevron-down');
        }
    }

    // 페이지 로드 시 내용 숨기기 (선택사항)
    // window.onload = function() {
    //     const content = document.getElementById('cart-content');
    //     if (content) {
    //         content.style.display = 'none';
    //     }
    // }

    document.addEventListener('DOMContentLoaded', function() {
        const cart = initialCartData || {};
        
        const menuListContainer = document.querySelector('.menu-list');
        const cartItemsContainer = document.querySelector('#cart-items');
        const totalPriceEl = document.querySelector('#total-price');
        const orderBtn = document.querySelector('#order-btn');
        // const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        // Initial UI update based on loaded data
        updateCartUI();

        menuListContainer.addEventListener('click', function(event) {
            if (!event.target.classList.contains('add-to-cart-btn')) {
                return;
            }

            const btn = event.target;
            const menuId = btn.dataset.menuId;
            const menuName = btn.dataset.menuName;
            const menuPrice = parseInt(btn.dataset.menuPrice);

            if (cart[menuId]) {
                cart[menuId].quantity += 1;
            } else {
                cart[menuId] = {
                    name: menuName,
                    price: menuPrice,
                    quantity: 1,
                };
            }
            
            updateCartUI();
        });

        function updateCartUI() {
            cartItemsContainer.innerHTML = '';
            let totalPrice = 0;

            if (Object.keys(cart).length === 0) {
                cartItemsContainer.innerHTML = '<p>장바구니가 비어 있습니다.</p>';
                totalPriceEl.textContent = '0';
                return;
            }

            const ul = document.createElement('ul');
            ul.classList.add('list-group');

            for (const menuId in cart) {
                const item = cart[menuId];
                totalPrice += item.price * item.quantity;
                
                const li = document.createElement('li');
                li.classList.add('list-group-item', 'd-flex', 'justify-content-between', 'align-items-center');
                li.innerHTML = `
                    <div>
                        ${item.name}
                        <br>
                        <small class="text-muted">${item.price.toLocaleString()}원 x ${item.quantity}</small>
                    </div>
                    <div>
                        <span class="fw-bold me-3">${(item.price * item.quantity).toLocaleString()}원</span>
                        <button class="btn btn-sm btn-outline-danger remove-from-cart-btn" data-menu-id="${menuId}">×</button>
                    </div>
                `;
                ul.appendChild(li);
            }
            cartItemsContainer.appendChild(ul);
            totalPriceEl.textContent = totalPrice.toLocaleString();
        }

        cartItemsContainer.addEventListener('click', function(event) {
            if (!event.target.classList.contains('remove-from-cart-btn')) {
                return;
            }
            const menuId = event.target.dataset.menuId;
            if (cart[menuId]) {
                delete cart[menuId];
                updateCartUI();
            }
        });

        orderBtn.addEventListener('click', function() {
            if (Object.keys(cart).length === 0) {
                alert('장바구니에 메뉴를 담아주세요!');
                return;
            }

            const cartItemsForBackend = Object.keys(cart).map(menuId => {
                return {
                    menu_id: menuId,
                    quantity: cart[menuId].quantity,
                    // options: {} // 옵션 기능 추가 시 이 부분 확장
                };
            });

            const dataToSend = {
                restaurant_pk: "{{ restaurant.pk }}",
                cart_items: cartItemsForBackend,
            };
            
            fetch("{% url 'orders:cart_view' %}", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: JSON.stringify(dataToSend)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    alert('주문이 성공적으로 접수되었습니다.');
                    window.location.href = data.redirect_url;
                } else {
                    alert('주문 실패: ' + (data.error || '알 수 없는 오류'));
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('주문 처리 중 오류가 발생했습니다.');
            });
        });
    });
