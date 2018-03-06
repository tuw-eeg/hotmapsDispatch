var data = source.data;                  
var filetext = ['name',
 'installed capacity (MW_th)',
 'efficiency th',
 'efficiency el',
 'investment costs (EUR/MW_th)',
 'OPEX fix (EUR/MWa)',
 'OPEX var (EUR/MWh)',
 'life time',
 'potential restriction (MW_th)',
 'renewable factor']
filetext = filetext.join();
for (i=0; i < data['name'].length; i++) {
    var currRow = [ data['name'][i].toString(),
				   data['installed capacity (MW_th)'][i].toString(),
				   data['efficiency th'][i].toString(),
				   data['efficiency el'][i].toString(),
				   data['investment costs (EUR/MW_th)'][i].toString(),
				   data['OPEX fix (EUR/MWa)'][i].toString(),
				   data['OPEX var (EUR/MWh)'][i].toString(),
				   data['life time'][i].toString(),
				   data['potential restriction (MW_th)'][i].toString(),
				   data['renewable factor'][i].toString()];
    var joined = currRow.join();
    filetext = filetext.concat('\n')
    filetext = filetext.concat(joined);
}	
var filename = 'input.csv';
var blob = new Blob([filetext], { type: 'text/csv;charset=utf-8;' });
if (navigator.msSaveBlob) {
	navigator.msSaveBlob(blob, filename);
}
else {
	var link = document.createElement("a");
	link = document.createElement('a')
	link.href = URL.createObjectURL(blob);
	link.download = filename
	link.target = "_blank";
	link.style.visibility = 'hidden';
	link.dispatchEvent(new MouseEvent('click'))
}