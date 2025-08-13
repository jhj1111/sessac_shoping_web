// =================================================
// ⭐ 리뷰 폼 별점 기능 (0.5 단위 지원) - 수정된 버전
// =================================================
const starRatingWrapper = document.querySelector('#star-rating-ui');
if (starRatingWrapper) {
    const starContainer = starRatingWrapper.querySelector('.star-container');
    const hiddenRatingInput = document.querySelector('#review-form #id_rating');
    const ratingText = starRatingWrapper.querySelector('.star-rating-text');

    // ✅ 스크립트 실행에 필요한 모든 요소가 있는지 확인하여 오류를 방지합니다.
    if (starContainer && hiddenRatingInput && ratingText) {
        let currentRating = hiddenRatingInput.value ? parseFloat(hiddenRatingInput.value) : 0;

        for (let i = 1; i <= 5; i++) {
            const starSpan = document.createElement('span');
            starSpan.classList.add('star');
            starSpan.dataset.value = i;
            starSpan.innerHTML = `<i class="bi bi-star"></i>`;
            starContainer.appendChild(starSpan);
        }
        const stars = starContainer.querySelectorAll('.star');

        const getRatingFromEvent = (e) => {
            const starElement = e.currentTarget;
            const starValue = parseFloat(starElement.dataset.value);
            const clickX = e.offsetX;
            const starWidth = starElement.clientWidth;
            return clickX < starWidth / 2 ? starValue - 0.5 : starValue;
        };

        const updateStarsVisual = (rating) => {
            stars.forEach(star => {
                const starValue = parseFloat(star.dataset.value);
                const icon = star.querySelector('i');
                if (rating >= starValue) {
                    icon.className = 'bi bi-star-fill text-warning';
                } else if (rating >= starValue - 0.5) {
                    icon.className = 'bi bi-star-half text-warning';
                } else {
                    icon.className = 'bi bi-star';
                }
            });
            ratingText.textContent = parseFloat(rating).toFixed(1);
        };

        stars.forEach(star => {
            star.addEventListener('mousemove', e => {
                updateStarsVisual(getRatingFromEvent(e));
            });
            star.addEventListener('mouseleave', () => {
                updateStarsVisual(currentRating);
            });
            star.addEventListener('click', e => {
                currentRating = getRatingFromEvent(e);
                hiddenRatingInput.value = currentRating;
                updateStarsVisual(currentRating);
            });
        });

        updateStarsVisual(currentRating);
    } else {
        console.error("리뷰 별점 UI를 위한 HTML 요소를 찾을 수 없습니다.");
    }
}