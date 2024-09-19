let scriptElement = document.createElement('script');
scriptElement.src = "../../static/sorting.js";

// Can specify whether the script should be executed asynchronously
// scriptElement.async = true;  // or false

// Appending the script to the <head> or <body>
document.body.appendChild(scriptElement); // or document.head.appendChild(script);
console.log("Script element added to the body");

// to add class "sortable" to each table with class "main-content-table"
var tables = document.getElementsByClassName('main-content-table');
for (var i = 0; i < tables.length; i++) {
	tables[i].classList.add('sortable');
}

// toggles menu open or close, and shifts main content if needed
function toggleMenu() {
    var sidebar = document.getElementById('sidebar');
    var mainContent = document.getElementById('main-content');
    var menuIcon = document.querySelector('.menu-icon');
	var mainContentAbove = document.getElementById('main-content-above');
    sidebar.classList.toggle('open');
    menuIcon.classList.toggle('open');
    mainContent.classList.toggle('main-content-shift');
	mainContentAbove.classList.toggle('main-content-shift');
    // add transition effect - when clicked on anywhere in the document, sidebar should close
    document.addEventListener('click', function(event) {
        if (!event.target.closest('#sidebar') && !event.target.closest('.menu-icon')) {
            sidebar.classList.remove('open');
            menuIcon.classList.remove('open');
            mainContent.classList.remove('main-content-shift');
			mainContentAbove.classList.remove('main-content-shift');
        }
    });
}

// toggles menu open or close, and shifts main content if needed
function templateToggleMenu() {
    const sidebar = documenttemplate.getElementById('sidebar');
    sidebar.classList.toggle('show');
}

var properties = ["JOB ID", "job type", "job description", "pay per hour", "start date", "end date", "is available"];

$.each( properties, function( i, val ) {
	
	var orderClass = '';

	$("#" + val).click(function(e){
		e.preventDefault();
		$('.filter__link.filter__link--active').not(this).removeClass('filter__link--active');
  		$(this).toggleClass('filter__link--active');
   		$('.filter__link').removeClass('asc desc');

   		if(orderClass == 'desc' || orderClass == '') {
    			$(this).addClass('asc');
    			orderClass = 'asc';
       	} else {
       		$(this).addClass('desc');
       		orderClass = 'desc';
       	}

		var parent = $(this).closest('.header__item');
    		var index = $(".header__item").index(parent);
		var $table = $('.table-content');
		var rows = $table.find('.table-row').get();
		var isSelected = $(this).hasClass('filter__link--active');
		var isNumber = $(this).hasClass('filter__link--number');
			
		rows.sort(function(a, b){

			var x = $(a).find('.table-data').eq(index).text();
    			var y = $(b).find('.table-data').eq(index).text();
				
			if(isNumber == true) {
    					
				if(isSelected) {
					return x - y;
				} else {
					return y - x;
				}

			} else {
			
				if(isSelected) {		
					if(x < y) return -1;
					if(x > y) return 1;
					return 0;
				} else {
					if(x > y) return -1;
					if(x < y) return 1;
					return 0;
				}
			}
    		});

		$.each(rows, function(index,row) {
			$table.append(row);
		});

		return false;
	});

});

// iska kaam abhi nahi hai, ignore it.
function toggleSubLinks() {
    var subLinks = document.getElementById('sub-links');
    subLinks.classList.toggle('open');
}

