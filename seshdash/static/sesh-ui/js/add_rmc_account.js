$(function(){
    // Handling the sensor adding on create rmc site-list
    var sensorContainers = $('.sensor-container'),
        firstSensorContainer = sensorContainers.first(),
        sensorListContainer = $('.sensor-list-container');
        addSensor = $('.add-another-sensor'),
        configureSensor = $('.configure-sensor'),
        removeSensor = $('.remove-sensor'),
        sensorSelectorInputs = $('.sensor-selector.sensor-changeable');


    changeConfigureForm(sensorSelectorInputs.first(), sensorSelectorInputs.first().val()); // Adding a form to the first sensor
    $('.configure-form-container').first().hide();

    InitializeSensors();

    // Getting the general structure of the container
    sensorHTMLStructure = sensorListContainer.children('.sensor-form-structure')[0].outerHTML;

    addSensor.click(function(){
        sensorListContainer.append(sensorHTMLStructure);
        removeSensor = $('.remove-sensor');
        configureSensor = $('.configure-sensor');
        sensorSelectorInputs = $('.sensor-selector');

        InitializeSensors();

    });


    function InitializeSensors() {
        removeSensor.click(function(){
            HandleRemoveSensor($(this));
        });

        configureSensor.unbind().click(function(){
            $(this).parent().parent().siblings('.configure-form-container').toggle();
        });

        sensorSelectorInputs.change(function(){
            HandleSensorSelectors($(this));
        })
    }

    function HandleRemoveSensor(removeSensorButton) {
        // Handles the deletion of a sensor in adding rmc account
        removeSensorButton.closest('.sensor-container').remove();
    }



    function HandleSensorSelectors(sensorSelector){
        // Handles the changing of the sensors select
        changeConfigureForm(sensorSelector, sensorSelector.val());
    }

    function changeConfigureForm(sensorSelectorInput, sensorType) {
        /* Replaces the content of the configure form container
            var sensorSelectorInput is used to determine the location to add the form and
            var sensorType is used to determine the type of the form to add.
        */
        var form;

        if (sensorType == 'Emon Th') {
            form = emonThForm
        }
        else if (sensorType == 'Emon Tx') {
            form = emonTxForm
        }
        else if (sensorType == 'BMV') {
            form = bmvForm
        }

        form = form.substring(1, (form.length -1)) // Removing the wrapper quotes

        sensorSelectorInput.parent().parent().parent()
                          .children('.configure-form-container').html(form).hide();

    }

});

