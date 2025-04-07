$(document).ready(function() {
    // Update bed availability on admin dashboard
    function updateBedStatus() {
        if ($('#bed-availability').length > 0) {
            $.ajax({
                url: '/api/beds',
                type: 'GET',
                dataType: 'json',
                success: function(data) {
                    $('#available-beds').text(data.available);
                    $('#total-beds').text(data.total);
                    
                    let bedList = '';
                    data.beds.forEach(function(bed) {
                        let statusClass = bed.occupied ? 'text-danger' : 'text-success';
                        let status = bed.occupied ? 'Occupied' : 'Available';
                        
                        bedList += `<tr>
                            <td>${bed.number}</td>
                            <td>${bed.ward}</td>
                            <td class="${statusClass}">${status}</td>
                        </tr>`;
                    });
                    
                    $('#bed-list').html(bedList);
                }
            });
        }
    }
    
    // Call initially and set interval
    updateBedStatus();
    setInterval(updateBedStatus, 30000);
    
    // Form validation for patient registration
    $('#patient-form').submit(function(e) {
        let isValid = true;
        
        // Simple validation example
        if ($('#patient-name').val().trim() === '') {
            $('#patient-name').addClass('is-invalid');
            isValid = false;
        } else {
            $('#patient-name').removeClass('is-invalid');
        }
        
        if ($('#patient-age').val().trim() === '' || isNaN($('#patient-age').val())) {
            $('#patient-age').addClass('is-invalid');
            isValid = false;
        } else {
            $('#patient-age').removeClass('is-invalid');
        }
        
        if (!isValid) {
            e.preventDefault();
        }
    });
});
