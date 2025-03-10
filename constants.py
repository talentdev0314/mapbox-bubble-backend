state_mapping = {
    "01": "AK", "02": "AL", "04": "AR", "05": "AZ", "06": "CA", "08": "CO",
    "09": "CT", "10": "DC", "11": "DE", "12": "FL", "13": "GA", "15": "HI",
    "16": "IA", "17": "ID", "18": "IL", "19": "IN", "20": "KS", "21": "KY",
    "22": "LA", "23": "MA", "24": "MD", "25": "ME", "26": "MI", "27": "MN",
    "28": "MO", "29": "MS", "30": "MT", "31": "NC", "32": "ND", "33": "NE",
    "34": "NH", "35": "NJ", "36": "NM", "37": "NV", "38": "NY", "39": "OH",
    "40": "OK", "41": "OR", "42": "PA", "44": "RI", "45": "SC", "46": "SD",
    "47": "TN", "48": "TX", "49": "UT", "50": "VA", "51": "VT", "53": "WA",
    "54": "WI", "55": "WV", "56": "WY"
}

yoy_list = [
    'college-degree-rate',
    'homeownership-rate',
    'housing-units',
    'housing-units-growth-rate',
    'income',
    'income-growth',
    'median-age',
    'mortgaged-home-%',
    'population',
    'population-growth',
    'poverty-rate',
    'remote-work-%'
]


mapping_dict = {
    "Home Value": {
        "slug": "home-value",
        "yearly-only": False,
        "format": {
            "prefix": "$",
            "display-suffix": "",
            "display-fixed": 0,
            "graph-suffix": "K",
            "graph-fixed": 1
        },
        "additional-data": []
    },
    "Home Value Growth (YoY)": {
        "slug": "home-value-growth-yoy",
        "yearly-only": False,
        "format": {
            "prefix": "",
            "display-suffix": "%",
            "display-fixed": 1,
            "graph-suffix": "%",
            "graph-fixed": 1
        },
        "additional-data": ["Last Year", "Current Year"]
    },
    "Overvalued %": {
        "slug": "overvalued-%", 
        "yearly-only": False,
        "format": {
            "prefix": "",
            "display-suffix": "%",
            "display-fixed": 1,
            "graph-suffix": "%",
            "graph-fixed": 1
        },
        "additional-data": ["Typical Home Price", "Fair Home Value"]
    },
    "Value/Income Ratio": {
        "slug": "value-to-income-ratio",
        "yearly-only": False,
        "format": {
            "prefix": "",
            "display-suffix": "",
            "display-fixed": 1,
            "graph-suffix": "",
            "graph-fixed": 2
        },
        "additional-data": ["Home Value", "Median HH. Income"]
    },
    "Mortgage Payment": {
        "slug": "mortgage-payment",
        "yearly-only": False,
        "format": {
            "prefix": "$",
            "display-suffix": "",
            "display-fixed": 0,
            "graph-suffix": "",
            "graph-fixed": 0
        },
        "additional-data": ["Principle & Interest", "Insurance, Taxes and misc costs", "Mortgage Rate"]
    },
    "Salary to Afford a House": {
        "slug": "salary-to-house",
        "yearly-only": False,
        "format": {
            "prefix": "$",
            "display-suffix": "",
            "display-fixed": 0,
            "graph-suffix": "",
            "graph-fixed": 0
        },
        "additional-data": [
            "Mortage Payment (Monthly)",
            "Mortage Payment (Annual)"
        ]
    },
    "Mtg Payment as % of income": {
        "slug": "mtg-payment-to-income",
        "yearly-only": False,
        "format": {
            "prefix": "",
            "display-suffix": "%",
            "display-fixed": 1,
            "graph-suffix": "%",
            "graph-fixed": 2
        },
        "additional-data": [
            "Yearly House Payment",
            "Median HH. Income",
            "Mortgage Rate"
        ]
    },
    "Property Tax Rate": {
        "slug": "property-tax-rate",
        "yearly-only": False,
        "format": {
            "prefix": "",
            "display-suffix": "%",
            "display-fixed": 1,
            "graph-suffix": "%",
            "graph-fixed": 2
        },
        "additional-data": []
    },
    "% Crash from 2007-12": {
        "slug": "%-crash-07-12",
        "yearly-only": True,
        "format": {
            "prefix": "$",
            "display-suffix": "%",
            "display-fixed": 1,
            "graph-suffix": "K",
            "graph-fixed": 1
        },
        "additional-data": []
    },
    "Home Value Growth (MoM)": {
        "slug": "home-value-growth-mom",
        "yearly-only": True,
        "format": {
            "prefix": "",
            "display-suffix": "%",
            "display-fixed": 2,
            "graph-suffix": "%",
            "graph-fixed": 2
        },
        "additional-data": []
    },
    "For Sale Inventory": {
        "slug": "for-sale-inventory",
        "yearly-only": False,
        "format": {
            "prefix": "",
            "display-suffix": "",
            "display-fixed": 0,
            "graph-suffix": "",
            "graph-fixed": 0
        },
        "additional-data": []
    },
    "Sale Inventory Growth (YoY)": {
        "slug": "for-sale-inventory",
        "yearly-only": False,
        "format": {
            "prefix": "",
            "display-suffix": "%",
            "display-fixed": 1,
            "graph-suffix": "%",
            "graph-fixed": 1
        },
        "additional-data": ["Last Year", "Current Year"]
    },
    "Inventory Surplus/Deficit": {
        "slug": "inventory-surplus-deficit",
        "yearly-only": False,
        "format": {
            "prefix": "",
            "display-suffix": "%",
            "display-fixed": 1,
            "graph-suffix": "%",
            "graph-fixed": 1
        },
        "additional-data": ["For Sale Inventory", "Long Term Average"]
    },
    "Price Cut %": {
        "slug": "price-cut-%",
        "yearly-only": False,
        "format": {
            "prefix": "",
            "display-suffix": "%",
            "display-fixed": 1,
            "graph-suffix": "%",
            "graph-fixed": 1
        },
        "additional-data": ["Listings with price cut", "Total Inventory"]
    },
    "Days on Market": {
        "slug": "days-on-market",
        "yearly-only": False,
        "format": {
            "prefix": "",
            "display-suffix": "",
            "display-fixed": 0,
            "graph-suffix": "",
            "graph-fixed": 0
        },
        "additional-data": []
    },
    "Days on Market Growth (YoY)": {
        "slug": "days-on-market-growth",
        "yearly-only": False,
        "format": {
            "prefix": "",
            "display-suffix": "%",
            "display-fixed": 1,
            "graph-suffix": "%",
            "graph-fixed": 1
        },
        "additional-data": ["Last Year", "Current Year"]
    },
    "Inventory as % of Houses": {
        "slug": "inventory-to-houses",
        "yearly-only": False,
        "format": {
            "prefix": "",
            "display-suffix": "%",
            "display-fixed": 1,
            "graph-suffix": "%",
            "graph-fixed": 1
        },
        "additional-data": [
            "Total Active Inventory",
            "Absentee Owned + Ownership HH's"
        ]
    },
    "Median Listing Price": {
        "slug": "median-listing-price",
        "yearly-only": False,
        "format": {
            "prefix": "$",
            "display-suffix": "",
            "display-fixed": 0,
            "graph-suffix": "",
            "graph-fixed": 0
        },
        "additional-data": []
    },
    "Median Listing Price (YoY)": {
        "slug": "median-listing-price-growth-yoy",
        "yearly-only": False,
        "format": {
            "prefix": "",
            "display-suffix": "%",
            "display-fixed": 1,
            "graph-suffix": "%",
            "graph-fixed": 2
        },
        "additional-data": ["Last Year", "Current Year"]
    },
    "New Listing Count": {
        "slug": "new-listing-count",
        "yearly-only": False,
        "format": {
            "prefix": "",
            "display-suffix": "",
            "display-fixed": 0,
            "graph-suffix": "",
            "graph-fixed": 0
        },
        "additional-data": []
    },
    "New Listing Count (YoY)": {
        "slug": "new-listing-count-growth-yoy",
        "yearly-only": False,
        "format": {
            "prefix": "",
            "display-suffix": "%",
            "display-fixed": 1,
            "graph-suffix": "%",
            "graph-fixed": 2
        },
        "additional-data": ["Last Year", "Current Year"]
    },
    "Sale Inventory Growth (MoM)": {
        "slug": "sale-inventory-growth-mom",
        "yearly-only": True,
        "format": {
            "prefix": "",
            "display-suffix": "%",
            "display-fixed": 1,
            "graph-suffix": "%",
            "graph-fixed": 1
        },
        "additional-data": ["Current Year"]
    },
    "Population": {
        "slug": "population",
        "yearly-only": False,
        "format": {
            "prefix": "",
            "display-suffix": "",
            "display-fixed": 0,
            "graph-suffix": "K",
            "graph-fixed": 1
        },
        "additional-data": []
    },
    "Median Household Income": {
        "slug": "income",
        "yearly-only": False,
        "format": {
            "prefix": "$",
            "display-suffix": "K",
            "display-fixed": 0,
            "graph-suffix": "K",
            "graph-fixed": 1
        },
        "additional-data": []
    },
    "Population Growth": {
        "slug": "population-growth",
        "yearly-only": True,
        "format": {
            "prefix": "",
            "display-suffix": "%",
            "display-fixed": 1,
            "graph-suffix": "%",
            "graph-fixed": 1
        },
        "additional-data": ["Last Year", "Current Year"]
    },
    "Income Growth": {
        "slug": "income-growth",
        "yearly-only": False,
        "format": {
            "prefix": "",
            "display-suffix": "%",
            "display-fixed": 1,
            "graph-suffix": "%",
            "graph-fixed": 1
        },
        "additional-data": ["Last Year", "Current Year"]
    },
    "Remote Work %": {
        "slug": "remote-work-%",
        "yearly-only": True,
        "format": {
            "prefix": "",
            "display-suffix": "%",
            "display-fixed": 1,
            "graph-suffix": "%",
            "graph-fixed": 1
        },
        "additional-data": ["Work From Home", "Total Employment"]
    },
    "College Degree Rate": {
        "slug": "college-degree-rate",
        "yearly-only": True,
        "format": {
            "prefix": "",
            "display-suffix": "%",
            "display-fixed": 1,
            "graph-suffix": "%",
            "graph-fixed": 1
        },
        "additional-data": ["Population with Bachelor's or Higher", "25+ Age Population"]
    },
    "Homeownership Rate": {
        "slug": "homeownership-rate",
        "yearly-only": True,
        "format": {
            "prefix": "",
            "display-suffix": "%",
            "display-fixed": 1,
            "graph-suffix": "%",
            "graph-fixed": 1
        },
        "additional-data": ["Ownership HH's", "Total Households"]
    },
    "Mortgaged Home %": {
        "slug": "mortgaged-home-%",
        "yearly-only": True,
        "format": {
            "prefix": "",
            "display-suffix": "%",
            "display-fixed": 0,
            "graph-suffix": "%",
            "graph-fixed": 2
        },
        "additional-data": ["Mortgaged Homes", "Ownership HH's"]
    },
    "Median Age": {
        "slug": "median-age",
        "yearly-only": True,
        "format": {
            "prefix": "",
            "display-suffix": "",
            "display-fixed": 1,
            "graph-suffix": "",
            "graph-fixed": 1
        },
        "additional-data": []
    },
    "Poverty Rate": {
        "slug": "poverty-rate",
        "yearly-only": True,
        "format": {
            "prefix": "",
            "display-suffix": "%",
            "display-fixed": 1,
            "graph-suffix": "%",
            "graph-fixed": 1
        },
        "additional-data": ["Population Living in Poverty", "Population"]
    },
    "Housing Units": {
        "slug": "housing-units",
        "yearly-only": True,
        "format": {
            "prefix": "",
            "display-suffix": "",
            "display-fixed": 0,
            "graph-suffix": "K",
            "graph-fixed": 1
        },
        "additional-data": []
    },
    "Housing Unit Growth Rate": {
        "slug": "housing-unit-growth-rate",
        "yearly-only": True,
        "format": {
            "prefix": "",
            "display-suffix": "%",
            "display-fixed": 1,
            "graph-suffix": "%",
            "graph-fixed": 2
        },
        "additional-data": ["Last Year", "Current Year"]
    },
    "Building Permits": {
        "slug": "building-permits",
        "yearly-only": False,
        "format": {
            "prefix": "",
            "display-suffix": "",
            "display-fixed": 0,
            "graph-suffix": "",
            "graph-fixed": 0
        },
        "additional-data": []
    },
    "Rental Rate": {
        "slug": "rental-rate",
        "yearly-only": False,
        "format": {
            "prefix": "$",
            "display-suffix": "",
            "display-fixed": 0,
            "graph-suffix": "",
            "graph-fixed": 0
        },
        "additional-data": []
    },
    "Rental For Houses": {
        "slug": "rental-for-houses",
        "yearly-only": False,
        "format": {
            "prefix": "$",
            "display-suffix": "",
            "display-fixed": 0,
            "graph-suffix": "",
            "graph-fixed": 0
        },
        "additional-data": []
    },
    "Cap Rate": {
        "slug": "cap-rate",
        "yearly-only": False,
        "format": {
            "prefix": "%",
            "display-suffix": "",
            "display-fixed": 1,
            "graph-suffix": "",
            "graph-fixed": 1
        },
        "additional-data": ["Gross Rent Income", "Expenses", "Net Rent Income", "Typical Home Price"]
    },
    "Vacancy Rate": {
        "slug": "vacancy-rate",
        "yearly-only": True,
        "format": {
            "prefix": "",
            "display-suffix": "%",
            "display-fixed": 1,
            "graph-suffix": "%",
            "graph-fixed": 2
        },
        "additional-data": ["Housing Units", "Vacancy Units"]
    },
    "Home Value to Rent Ratio": {
        "slug": "home-value-to-rent-ratio",
        "yearly-only": False,
        "format": {
            "prefix": "",
            "display-suffix": "",
            "display-fixed": 1,
            "graph-suffix": "",
            "graph-fixed": 2
        },
        "additional-data": ["Home Values", "Annual Rent for Houses"]
    },
    "Rent as % of Income": {
        "slug": "rent-to-income",
        "yearly-only": False,
        "format": {
            "prefix": "",
            "display-suffix": "%",
            "display-fixed": 1,
            "graph-suffix": "%",
            "graph-fixed": 2
        },
        "additional-data": ["Yearly Apartment Rent", "Med. HH. Income"]
    },
    "Shadow Inventory %": {
        "slug": "shadow-inventory",
        "yearly-only": True,
        "format": {
            "prefix": "",
            "display-suffix": "%",
            "display-fixed": 1,
            "graph-suffix": "%",
            "graph-fixed": 2
        },
        "additional-data": ["Absentee Owned Units", "Absentee Owned + Ownership HH's"]
    },
    "Migration Total": {
        "slug": "migration-total",
        "yearly-only": True,
        "format": {
            "prefix": "",
            "display-suffix": "",
            "display-fixed": 0,
            "graph-suffix": "K",
            "graph-fixed": 1
        },
        "additional-data": []
    },
    "Migration % of Population": {
        "slug": "migration-to-population",
        "yearly-only": True,
        "format": {
            "prefix": "",
            "display-suffix": "%",
            "display-fixed": 1,
            "graph-suffix": "%",
            "graph-fixed": 1
        },
        "additional-data": ["Migration Total", "Population"]
    },
    "Rent Growth (YoY)": {
        "slug": "rent-growth-yoy",
        "yearly-only": False,
        "format": {
            "prefix": "",
            "display-suffix": "%",
            "display-fixed": 1,
            "graph-suffix": "%",
            "graph-fixed": 2
        },
        "additional-data": ["Last Year", "Current Year"]
    },
    "Typical Home Price": {
        "slug": "home-value",
        "format": {
            "prefix": "$",
            "display-suffix": "",
            "display-fixed": 0,
            "graph-suffix": "",
            "graph-fixed": 0
        },
    },
    "Fair Home Value": {
        "slug": "fair-home-value",
        "format": {
            "prefix": "$",
            "display-suffix": "K",
            "display-fixed": 1,
            "graph-suffix": "K",
            "graph-fixed": 1
        },
    },
    "Mortgage Rate": {
        "slug": "mortgage-rate",
        "format": {
            "prefix": "",
            "display-suffix": "",
            "display-fixed": 2,
            "graph-suffix": "",
            "graph-fixed": 2
        },
    },
    "Insurance, Taxes and mic costs": {
        "slug": "insurance-taxes-misc-costs",
        "format": {
            "prefix": "",
            "display-suffix": "",
            "display-fixed": 0,
            "graph-suffix": "",
            "graph-fixed": 0
        },
    },
    "Principle & Interest": {
        "slug": "principle-interest",
        "format": {
            "prefix": "",
            "display-suffix": "",
            "display-fixed": 0,
            "graph-suffix": "",
            "graph-fixed": 0
        },
    },
    "Mortgage Payment (Monthly)": {
        "slug": "mortgage-payment",
        "format": {
            "prefix": "$",
            "display-suffix": "",
            "display-fixed": 0,
            "graph-suffix": "",
            "graph-fixed": 0
        },
    },
    "Mortgage Payment (Annual)": {
        "slug": "mortgage-payment-annual",
        "format": {
            "prefix": "$",
            "display-suffix": "",
            "display-fixed": 0,
            "graph-suffix": "",
            "graph-fixed": 0
        },
    },
    "Yearly House Payment": {
        "slug": "yearly-house-payment",
        "format": {
            "prefix": "$",
            "display-suffix": "",
            "display-fixed": 0,
            "graph-suffix": "",
            "graph-fixed": 0
        },
    },
    "Long Term Average": {
        "slug": "long-term-average",
        "format": {
            "prefix": "",
            "display-suffix": "",
            "display-fixed": 0,
            "graph-suffix": "",
            "graph-fixed": 0
        },
    },
    "Total Inventory": {
        "slug": "total-inventory",
        "format": {
            "prefix": "",
            "display-suffix": "",
            "display-fixed": 0,
            "graph-suffix": "",
            "graph-fixed": 0
        },
    },
    "Listings with price cut": {
        "slug": "listings-with-price-cut",
        "format": {
            "prefix": "",
            "display-suffix": "",
            "display-fixed": 0,
            "graph-suffix": "",
            "graph-fixed": 0
        },
    },
    "Absentee Owned + Ownership HH's": {
        "slug": "absentee+ownership",
        "format": {
            "prefix": "",
            "display-suffix": "",
            "display-fixed": 0,
            "graph-suffix": "",
            "graph-fixed": 0
        },
    },
    "Total Active Inventory": {
        "slug": "total-active-inventory",
        "format": {
            "prefix": "",
            "display-suffix": "",
            "display-fixed": 0,
            "graph-suffix": "",
            "graph-fixed": 0
        },
    },
    "Total Employment": {
        "slug": "total-employment",
        "format": {
            "prefix": "",
            "display-suffix": "",
            "display-fixed": 0,
            "graph-suffix": "",
            "graph-fixed": 0
        },
    },
    "Work From Home": {
        "slug": "work-from-home",
        "format": {
            "prefix": "",
            "display-suffix": "",
            "display-fixed": 0,
            "graph-suffix": "",
            "graph-fixed": 0
        },
    },
    "25+ Age Population": {
        "slug": "25-age-population",
        "format": {
            "prefix": "",
            "display-suffix": "",
            "display-fixed": 0,
            "graph-suffix": "",
            "graph-fixed": 0
        },
    },
    "Population with Bachelor's or Higher": {
        "slug": "population-with-bachelor-or-higher",
        "format": {
            "prefix": "",
            "display-suffix": "",
            "display-fixed": 0,
            "graph-suffix": "",
            "graph-fixed": 0
        },
    },
    "Total Households": {
        "slug": "total-households",
        "format": {
            "prefix": "",
            "display-suffix": "",
            "display-fixed": 0,
            "graph-suffix": "",
            "graph-fixed": 0
        },
    },
    "Ownership HH's": {
        "slug": "ownership-hh",
        "format": {
            "prefix": "",
            "display-suffix": "",
            "display-fixed": 0,
            "graph-suffix": "",
            "graph-fixed": 0
        },
    },
    "Mortgaged Homes": {
        "slug": "mortgaged-homes",
        "format": {
            "prefix": "",
            "display-suffix": "",
            "display-fixed": 0,
            "graph-suffix": "",
            "graph-fixed": 0
        },
    },
    "Population Living in Poverty": {
        "slug": "population-living-in-poverty",
        "format": {
            "prefix": "",
            "display-suffix": "",
            "display-fixed": 0,
            "graph-suffix": "",
            "graph-fixed": 0
        },
    },
    "Net Rent Income": {
        "slug": "net-rent-income",
        "format": {
            "prefix": "$",
            "display-suffix": "",
            "display-fixed": 0,
            "graph-suffix": "",
            "graph-fixed": 0
        },
    },
    "Expenses": {
        "slug": "expenses",
        "format": {
            "prefix": "$",
            "display-suffix": "",
            "display-fixed": 0,
            "graph-suffix": "",
            "graph-fixed": 0
        },
    },
    "Gross Rent Income": {
        "slug": "gross-rent-income",
        "format": {
            "prefix": "$",
            "display-suffix": "",
            "display-fixed": 0,
            "graph-suffix": "",
            "graph-fixed": 0
        },
    },
    "Vacancy Units": {
        "slug": "vacancy-units",
        "format": {
            "prefix": "$",
            "display-suffix": "",
            "display-fixed": 0,
            "graph-suffix": "",
            "graph-fixed": 0
        },
    },
    "Annual Rent for Houses": {
        "slug": "annual-rent-for-houses",
        "format": {
            "prefix": "$",
            "display-suffix": "",
            "display-fixed": 0,
            "graph-suffix": "",
            "graph-fixed": 0
        },
    },
    "Med. HH. Income": {
        "slug": "income",
        "format": {
            "prefix": "$",
            "display-suffix": "",
            "display-fixed": 0,
            "graph-suffix": "",
            "graph-fixed": 0
        },
    },
    "Yearly Apartment Rent": {
        "slug": "yearly-apartment-rent",
        "format": {
            "prefix": "$",
            "display-suffix": "",
            "display-fixed": 0,
            "graph-suffix": "",
            "graph-fixed": 0
        },
    },
    "Absentee Owned Units": {
        "slug": "absentee-owned-units",
        "format": {
            "prefix": "",
            "display-suffix": "",
            "display-fixed": 0,
            "graph-suffix": "",
            "graph-fixed": 0
        },
    },
}