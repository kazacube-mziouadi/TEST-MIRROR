function roundTo(n, digits) {
    let negative = false;
    if (digits === undefined) {
        digits = 0;
    }
    if (n < 0) {
        negative = true;
        n = n * -1;
    }
    let multiplicator = Math.pow(10, digits);
    n = parseFloat((n * multiplicator).toFixed(11));
    n = (Math.round(n) / multiplicator).toFixed(digits);
    if (negative) {
        n = (n * -1).toFixed(digits);
    }
    const floatStringSplit = n.toString().split('.');
    const floatStringDecimalPart = floatStringSplit[1];
    if (parseInt(floatStringDecimalPart) === 0) {
        return floatStringSplit[0];
    } else {
        let decimalIndex = digits - 1;
        while (decimalIndex >= 0) {
            if (parseInt(floatStringDecimalPart[decimalIndex]) !== 0) {
                return floatStringSplit[0] + '.' + floatStringDecimalPart.substring(0, decimalIndex + 1)
            }
            decimalIndex--;
        }
        return n;
    }
}

// Drag'n'drop file area
document.addEventListener("DOMContentLoaded", function(event) {
  $(document).on("ready", ".o_kanban_record", function(e) {
     $(e).trigger("hover");
  });
  $(document).on('drag dragstart dragend dragover dragenter dragleave drop', '.drag_and_drop_area', function(e) {
     e.preventDefault();
     e.stopPropagation();
  })
  $(document).on('dragover dragenter', '.drag_and_drop_area', function(e) {
    $('.drag_and_drop_area').addClass('is-dragover');
  })
  $(document).on('dragleave dragend drop', '.drag_and_drop_area', function(e) {
    $('.drag_and_drop_area').removeClass('is-dragover');
  })
  $(document).on('drop', '.drag_and_drop_area', function(e) {
    inputFile = $('.my_fab_drag_and_drop').find('input[type="file"]')[0];
    inputFile.files = e.originalEvent.dataTransfer.files;
    $(inputFile).change();
  });
});

