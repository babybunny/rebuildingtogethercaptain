function updateCost(value, unitCost, target_id) {
    target = document.getElementById(target_id);
    var v = parseInt(value); 
    if (v > 0) { 
	var t = unitCost * value; 
	target.innerHTML = t.toFixed(2); 
    } else { 
	target.innerHTML = ''; 
    }
    var subtotal = 0.0;
    var items = document.getElementsByName('item_total');
    for (i in items) {
	item = items[i];
	item_total = parseFloat(item.innerHTML);
	if (item_total) {
	    subtotal = subtotal + item_total;
	}
    }
    subtotal_span = document.getElementById('sub_total');
    subtotal_span.innerHTML = subtotal.toFixed(2);
}