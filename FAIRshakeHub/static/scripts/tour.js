var tour = new Tour({
  name: "FAIRshake Tour",
  debug: true,
  backdrop: true,
  steps: [
    {
      path: '/',
      element: "#search",
      title: "Searching FAIRshake",
      content: "FAIRshake lets you search everything from the home page, let's try searching for flybase!",
      onNext: function() {
        document.location.href = '/?q=flybase';
        return (new $.Deferred()).promise();
      },
    },
    {
      // path: '/?q=flybase',
      element: ".panel:first",
      title: "Search results",
      content: "FAIRshake presents the results as cards for each element in the database",
    },
    {
      // path: '/?q=flybase',
      element: ".panel:first .image-link img",
      title: "Image",
      content: "The image is registered by users for quickly identifying objects",
    },
    {
      // path: '/?q=flybase',
      element: ".panel:first .caption",
      title: "Description",
      content: "A short title and description is provided to further identify the object.",
    },
    {
      // path: '/?q=flybase',
      element: ".panel:first .label",
      title: "Object Type",
      content: "The type of Digital Object is identified.",
    },
    {
      // path: '/?q=flybase',
      element: ".panel:first .insignia",
      title: "Insignia",
      content: "The FAIRshake Insignia is displayed illustrating how FAIR the object is, red boxes indicate metrics which could not be asserted, while blue boxes indicate those which could.",
    },
  ],
});