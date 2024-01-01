document.addEventListener('DOMContentLoaded', function() {
    filterTable();
});

function filterTable() {
    var now = new Date();
    var n_rows = 4;
    var rows = document.querySelectorAll("#timeTable tr[data-time]");
    var upcomingRows = [];

    // Collect and sort the times
    rows.forEach(function(row) {
        var rowTime = new Date(row.getAttribute('data-time'));
        if (rowTime > now) {
            upcomingRows.push({ time: rowTime, row: row });
        }
    });

    upcomingRows.sort(function(a, b) {
        return a.time - b.time;
    });

    // Hide all rows initially
    rows.forEach(function(row) {
        row.style.display = 'none';
    });

    // Show only the next three instances
    for (var i = 0; i < upcomingRows.length && i < n_rows; i++) {
        upcomingRows[i].row.style.display = '';
    }
}