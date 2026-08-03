new DataTable('#requestsTable', {
    columnDefs: [
        { className: 'text-right', targets: [0] },
        { className: 'text-center', targets: [1] },
        { className: 'text-center', targets: [$('#requestsTable th:contains("Status")').index()] },
        { className: 'dt-head-center', targets: '_all' },
    ],
    scrollX: true,
});
