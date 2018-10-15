var data = source.data;
var filename = data['filename'][0]
var path = 'download/static/'.concat(data['id'][0]).concat('/').concat(filename)
fetch(path, {cache: 'no-store'}).then(response => response.blob())
                    .then(blob => {
                        //addresses IE
                        if (navigator.msSaveBlob) {
                            navigator.msSaveBlob(blob, filename);
                        }

                        else {
                            var link = document.createElement("a");
                            link = document.createElement('a')
                            link.href = URL.createObjectURL(blob);
                            window.open(link.href, '_blank');

                            link.download = filename
                            link.target = "_blank";
                            link.style.visibility = 'hidden';
                            link.dispatchEvent(new MouseEvent('click'))
                            URL.revokeObjectURL(url);
                        }
                        return response.text();
                    });