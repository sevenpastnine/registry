import tailwindColors from 'tailwindcss/colors'
import tailwindForms from '@tailwindcss/forms'
import tailwindTypography from '@tailwindcss/typography'

function colorWithOpacity(variableName) {
    return ({ opacityValue }) => {
        if (opacityValue !== undefined) {
            return `rgba(var(${variableName}), ${opacityValue})`
        }
        return `rgb(var(${variableName}))`
    }
}

export default {
    plugins: [
        tailwindTypography,
        tailwindForms
    ],
    content: [
        "./backend/**/*.{html,js}",
        "./frontend/**/*.{html,js,jsx,ts,tsx}",
    ],
    theme: {
        fontSize: {
            'xs': '.75rem',
            'sm': '.875rem',
            'base': '1rem',
            'lg': '1.15rem',
            'xl': '1.25rem',
            '2xl': '2rem',
            '3xl': '2.5rem',
            '4xl': '3rem',
            '5xl': '3.5rem',
            '6xl': '5rem',
            '7xl': '6rem',
            '8xl': '7rem',
        },
        container: {
            center: true,
            padding: {
                DEFAULT: '1rem',
                sm: '1rem',
                md: '1rem',
                lg: '2rem',
                xl: '2rem',
                '2xl': '4rem',
            },
            screens: {
                sm: '640px',
                md: '768px',
                lg: '1024px',
                xl: '1280px',
                '2xl': '1280px',
            },
        },
        extend: {
            colors: {
                'primary': {
                    '50': colorWithOpacity("--color-primary-50"),
                    '100': colorWithOpacity("--color-primary-100"),
                    '200': colorWithOpacity("--color-primary-200"),
                    '300': colorWithOpacity("--color-primary-300"),
                    '400': colorWithOpacity("--color-primary-400"),
                    '500': colorWithOpacity("--color-primary-500"),
                    '600': colorWithOpacity("--color-primary-600"),
                    '700': colorWithOpacity("--color-primary-700"),
                    '800': colorWithOpacity("--color-primary-800"),
                    '900': colorWithOpacity("--color-primary-900"),
                    '950': colorWithOpacity("--color-primary-950"),
                    'DEFAULT': colorWithOpacity("--color-primary-DEFAULT"),
                },
                'secondary': tailwindColors.zinc,
                'muted': tailwindColors.zinc[500],
                'error': tailwindColors.red[500],
                'beware': tailwindColors.orange[500],
                'warning': tailwindColors.yellow[500],
                'success': tailwindColors.green[500],
                'info': tailwindColors.blue[500],
            },
            spacing: {
                '1/2gap': '0.5rem',
                'gap': '1rem',
                '2gap': '2rem',
                '3gap': '3rem',
                '4gap': '4rem',
                '5gap': '5rem',
                '6gap': '6rem',
                '7gap': '7rem',
                '8gap': '8rem',
            },
            fontFamily: {
                sans: ['Inter', 'Arial', 'Helvetica', 'sans-serif'],
                mono: ['monospace'],
            },
            fontVariationSettings: {
                'wght': {
                    400: '400',
                    500: '500',
                    700: '700',
                },
            },
            borderColor: {
                DEFAULT: tailwindColors.gray[200],
            },
            typography: (theme) => ({
                DEFAULT: {
                    css: {
                        color: 'black',
                        a: {
                            color: theme('colors.primary'),
                            fontWeight: '400',
                        },
                        b: {
                            color: 'black',
                        },
                        code: {
                            '&::before': {
                                content: '"" !important',
                            },
                            '&::after': {
                                content: '"" !important',
                            },
                        }
                    }
                }
            })
        }
    }
}
