

build: EwsToFullcalendar.cs deps
	mcs -target:winexe -out:./bin/EwsToFullcalendar.exe -r:./bin/Microsoft.Exchange.WebServices.dll EwsToFullcalendar.cs

lib:
	mkdir lib

bin:
	mkdir bin

deps: ews

ews: lib bin
	test -d ./lib/Microsoft.Exchange.WebServices.2.2 || nuget install Microsoft.Exchange.WebServices -OutputDirectory lib
	test -f ./bin/Microsoft.Exchange.WebServices.dll || cp ./lib/Microsoft.Exchange.WebServices.2.2/lib/40/Microsoft.Exchange.WebServices.dll ./bin/Microsoft.Exchange.WebServices.dll

run:
	mono ./bin/EwsToFullcalendar.exe
