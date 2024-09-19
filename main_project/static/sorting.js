document.addEventListener('click', function (e) {
    try {
        function findElementRecursive(element, tag) {
            return element.nodeName === tag ? element :
                findElementRecursive(element.parentNode, tag)
        }
        var descending_th_class = ' dir-d '
        var ascending_th_class = ' dir-u '
        var ascending_table_sort_class = 'asc'
        var regex_dir = / dir-(u|d) /
        var regex_table = /\bsortable\b/
        var alt_sort = e.shiftKey || e.altKey
        var element = findElementRecursive(e.target, 'TH')
        var tr = findElementRecursive(element, 'TR')
        var table = findElementRecursive(tr, 'TABLE')
        function reClassify(element, dir) {
            element.className = element.className.replace(regex_dir, '') + dir
        }
        function getValue(element) {
            return (
                (alt_sort && element.getAttribute('data-sort-alt')) ||
                element.getAttribute('data-sort') || element.innerText
            )
        }
        if (regex_table.test(table.className)) {
            var column_index
            var nodes = tr.cells
            for (var i = 0; i < nodes.length; i++) {
                if (nodes[i] === element) {
                    column_index = element.getAttribute('data-sort-col') || i
                } else {
                    reClassify(nodes[i], '')
                }
            }
            var dir = descending_th_class
            if (
                element.className.indexOf(descending_th_class) !== -1 ||
                (table.className.indexOf(ascending_table_sort_class) !== -1 &&
                    element.className.indexOf(ascending_th_class) == -1)
            ) {
                dir = ascending_th_class
            }
            reClassify(element, dir)
            var org_tbody = table.tBodies[0]
            var rows = [].slice.call(org_tbody.rows, 0)
            var reverse = dir === ascending_th_class
            rows.sort(function (a, b) {
                var x = getValue((reverse ? a : b).cells[column_index])
                var y = getValue((reverse ? b : a).cells[column_index])
                return isNaN(x - y) ? x.localeCompare(y) : x - y
            })
            var clone_tbody = org_tbody.cloneNode()
            while (rows.length) {
                clone_tbody.appendChild(rows.splice(0, 1)[0])
            }
            table.replaceChild(clone_tbody, org_tbody)
        }
    } catch (error) {
    }
});