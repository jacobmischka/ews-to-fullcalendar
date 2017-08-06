using System;
using Microsoft.Exchange.WebServices.Data;

public class EwsToFullcalendar {
	public static void Main(string[] args) {
		ExchangeService service = GetExchangeService();

		FolderId calendar = new FolderId("")
	}

	static ExchangeService GetExchangeService() {
		string username = System.Environment.GetEnvironmentVariable("EWS_USERNAME");
		string password = System.Environment.GetEnvironmentVariable("EWS_PASSWORD");
		string domain = System.Environment.GetEnvironmentVariable("EWS_DOMAIN");
		string server = System.Environment.GetEnvironmentVariable("EWS_SERVER");

		ExchangeService service = new ExchangeService(ExchangeVersion.Exchange2013_SP1);
		service.TraceEnabled = true;
		service.TraceFlags = TraceFlags.All;
		service.TraceListener = new TraceListener();
		service.Url = new Uri("https://" + server + "/EWS/Exchange.asmx");
		service.Credentials = new WebCredentials(username, password, domain);

		return service;
	}
}

class TraceListener : ITraceListener {
	#region ITraceListener Members
	public void Trace(string traceType, string traceMessage) {
		System.IO.File.WriteAllText(traceType + ".xml", traceMessage);
	}
	#endregion
}
