# usedcararoundme

UsedCarAroundMe is a static website that simulates a used car browsing platform similar to AutoTrader.com. It uses the NHTSA vehicle database API to retrieve vehicle specifications and metadata.

## Features

- Browse vehicles by make, model, and year
- View detailed vehicle specifications from the NHTSA database
- See estimated price calculations (simulated for demonstration)
- Responsive design that works on all devices
- Fallback data when the NHTSA API is unavailable or experiencing CORS issues

## Live Demo

Visit [https://nopgae.github.io/usedcararoundme](https://nopgae.github.io/usedcararoundme) to see the live demo.

## Project Structure

```
usedcararoundme/
├── index.html              # Main HTML file
├── css/
│   ├── styles.css          # Custom styles
│   └── bootstrap.min.css   # Bootstrap CSS (from CDN)
├── js/
│   ├── app.js              # Main application logic
│   ├── api.js              # API handling functions
│   └── fallback-data.js    # Fallback data for when API is unavailable
├── images/
│   ├── logo.png            # Site logo
│   └── car-placeholder.jpg # Default car image
├── favicon.ico             # Site favicon
└── README.md               # Project documentation
```

## Setup Instructions

### Prerequisites

- Git installed on your computer
- A GitHub account
- Basic knowledge of HTML, CSS, and JavaScript
- A text editor (e.g., VS Code, Sublime Text)

### Step 1: Create a GitHub Repository

1. Log in to your GitHub account.
2. Click the "+ New" button to create a new repository.
3. Name your repository "usedcararoundme".
4. Set the repository to "Public".
5. Check the "Add a README file" option.
6. Click "Create repository".

### Step 2: Clone the Repository

1. On your repository page, click the "Code" button and copy the HTTPS URL.
2. Open a terminal or command prompt on your computer.
3. Navigate to the directory where you want to store your project.
4. Run the following command to clone the repository:

```bash
git clone https://github.com/nopgae/usedcararoundme.git
cd usedcararoundme
```

### Step 3: Add Project Files

1. Create the directory structure as shown above.
2. Copy all the HTML, CSS, and JavaScript files into their respective directories.

### Step 4: Add Images

1. Create an `images` directory.
2. Add a logo image (logo.png) and a car placeholder image (car-placeholder.jpg).
3. You can use placeholder services or create your own images.

Sample logo command:
```bash
# Example using ImageMagick to create a simple logo
convert -size 200x200 -background transparent -fill blue -font Arial -pointsize 72 label:UC images/logo.png
```

Sample placeholder image command:
```bash
# Example using curl to download a placeholder
curl -o images/car-placeholder.jpg https://via.placeholder.com/800x450.jpg?text=Vehicle+Image
```

### Step 5: Commit and Push Your Changes

1. Add all the files to Git:

```bash
git add .
```

2. Commit the changes:

```bash
git commit -m "Initial commit for UsedCarAroundMe website"
```

3. Push the changes to GitHub:

```bash
git push origin main
```

### Step 6: Deploy on GitHub Pages

1. Go to your repository on GitHub.
2. Click on "Settings".
3. Scroll down to the "GitHub Pages" section.
4. Under "Source", select "main" branch and "/" (root) folder.
5. Click "Save".
6. GitHub will provide you with a URL where your site is published (usually https://yourusername.github.io/usedcararoundme/).

## Limitations and Future Enhancements

### Current Limitations

1. **Static Website**: The website is entirely client-side, which limits some functionality.
2. **NHTSA API Limitations**: The NHTSA API doesn't provide all the data we need (like pricing), so we simulate some data.
3. **CORS Issues**: The NHTSA API may experience CORS issues in certain browsers, requiring fallback data.
4. **Limited Search**: Only basic make/model/year searches are supported.
5. **No User Accounts**: The site doesn't support user accounts or saved searches.

### Potential Future Enhancements

1. **Backend Integration**: Add a Node.js backend to enhance functionality.
2. **Real Pricing Data**: Integrate with a vehicle valuation API for real pricing.
3. **User Accounts**: Allow users to create accounts and save favorite vehicles.
4. **Advanced Search**: Add more search filters like price range, body style, etc.
5. **Map Integration**: Show vehicles available near the user's location.
6. **VIN Lookup**: Allow users to search by VIN for specific vehicle information.
7. **Dealer Integration**: Allow dealers to list their inventory on the platform.

## Troubleshooting

### API Issues

If the NHTSA API is unavailable or experiencing CORS issues:

1. The application will automatically switch to fallback data.
2. A modal will appear informing you of the issue.
3. You can click "Retry Connection" to attempt to reconnect to the API.

### Deployment Issues

If your site isn't showing up on GitHub Pages:

1. Make sure your repository is public.
2. Check that you've correctly set the GitHub Pages source to the main branch.
3. Wait a few minutes - GitHub Pages can take some time to deploy.

## License

This project is open source and available under the [MIT License](LICENSE).

## Acknowledgments

- Built with [Bootstrap](https://getbootstrap.com/)
- Vehicle data from [NHTSA](https://vpic.nhtsa.dot.gov/api/)