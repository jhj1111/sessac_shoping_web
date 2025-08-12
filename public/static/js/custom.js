
// isotope js
var $grid;

$(window).on('load', function() {
    $grid = $(".grid").isotope({
        itemSelector: ".all",
        percentPosition: false,
        masonry: {
            columnWidth: ".all"
        }
    });

    $('.filters_menu li').click(function () {
        $('.filters_menu li').removeClass('active');
        $(this).addClass('active');

        var data = $(this).attr('data-filter');
        $grid.isotope({
            filter: data
        });
    });
});

// ===== 여기부터 추가 =====
    function showLimitedItems() {
        var $items = $grid.find('.all');
        $items.hide().slice(0, 6).show();
        $grid.isotope('layout');
        $('#loadMore').show();
    }

    // 처음 로드시 전체 6개만 표시
    showLimitedItems();

    // 필터 버튼 클릭 시
    $('.filters_menu li').on('click', function () {
        var filterValue = $(this).attr('data-filter');

        if (filterValue === '*') {
            showLimitedItems();
        } else {
            $grid.find(filterValue).show();
            $grid.isotope({ filter: filterValue });
            $('#loadMore').hide();
        }
    });
    // ===== 여기까지 추가 =====


// nice select
$(document).ready(function() {
    $('select').niceSelect();
  });

/** google_map js **/
function myMap() {
    var mapProp = {
        center: new google.maps.LatLng(40.712775, -74.005973),
        zoom: 18,
    };
    var map = new google.maps.Map(document.getElementById("googleMap"), mapProp);
}

// client section owl carousel
$(".client_owl-carousel").owlCarousel({
    loop: true,
    margin: 0,
    dots: false,
    nav: true,
    navText: [],
    autoplay: true,
    autoplayHoverPause: true,
    navText: [
        '<i class="fa fa-angle-left" aria-hidden="true"></i>',
        '<i class="fa fa-angle-right" aria-hidden="true"></i>'
    ],
    responsive: {
        0: {
            items: 1
        },
        768: {
            items: 2
        },
        1000: {
            items: 2
        }
    }
});
$(window).on('load', function() {
  var $grid = $(".grid").isotope({
    itemSelector: ".filter-item",
    layoutMode: 'fitRows'
  });

  function showLimitedItems(filter) {
    var $items;
    if (filter === '*' || filter === '.all') {
      $items = $grid.find('.filter-item');
    } else {
      $items = $grid.find(filter);
    }
    $items.hide().slice(0, 6).show();
    $grid.isotope('layout');
  }

  // 초기에는 전체 6개만 보여주기
  showLimitedItems('*');

  $('.filters_menu li').on('click', function () {
    $('.filters_menu li').removeClass('active');
    $(this).addClass('active');

    var filterValue = $(this).attr('data-filter');
    if (filterValue === '*') filterValue = '.all';

    $grid.isotope({ filter: filterValue });
    showLimitedItems(filterValue);
  });
});