frappe.listview_settings["Enrollment"] = {
  get_indicator: function (doc) {
    if (doc.status === "Upcoming") {
      return ["Upcoming", "blue", "status,=,Upcoming"];
    } else if (doc.status === "Active") {
      return ["Active", "green", "status,=,Active"];
    } else if (doc.status === "Expired") {
      return ["Expired", "red", "status,=,Expired"];
    }
	},
};
