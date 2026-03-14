#!/usr/bin/env python3
"""Analyze and categorize project dependencies."""

import json
import sys
from pathlib import Path

def analyze_node_deps(package_path='package.json'):
    """Analyze Node.js dependencies."""
    try:
        with open(package_path) as f:
            pkg = json.load(f)
    except FileNotFoundError:
        return None

    deps = pkg.get('dependencies', {})
    dev_deps = pkg.get('devDependencies', {})

    categories = {
        'framework': [],
        'ui': [],
        'database': [],
        'testing': [],
        'build': [],
        'lint': [],
        'utility': [],
        'other': []
    }

    framework_patterns = ['react', 'vue', 'angular', 'svelte', 'next', 'nuxt', 'express', 'fastify', 'koa']
    ui_patterns = ['tailwind', 'bootstrap', 'material-ui', 'antd', 'chakra', 'styled-components']
    db_patterns = ['mongoose', 'sequelize', 'prisma', 'typeorm', 'mongodb', 'redis', 'postgres']
    test_patterns = ['jest', 'vitest', 'cypress', 'playwright', 'mocha', 'jasmine', '@testing-library']
    build_patterns = ['webpack', 'vite', 'rollup', 'esbuild', 'parcel', 'turbo']
    lint_patterns = ['eslint', 'prettier', 'stylelint', 'commitlint', 'husky']

    all_deps = {**deps, **dev_deps}

    for dep in all_deps:
        dep_lower = dep.lower()
        categorized = False

        for pattern in framework_patterns:
            if pattern in dep_lower:
                categories['framework'].append(dep)
                categorized = True
                break

        if not categorized:
            for pattern in ui_patterns:
                if pattern in dep_lower:
                    categories['ui'].append(dep)
                    categorized = True
                    break

        if not categorized:
            for pattern in db_patterns:
                if pattern in dep_lower:
                    categories['database'].append(dep)
                    categorized = True
                    break

        if not categorized:
            for pattern in test_patterns:
                if pattern in dep_lower:
                    categories['testing'].append(dep)
                    categorized = True
                    break

        if not categorized:
            for pattern in build_patterns:
                if pattern in dep_lower:
                    categories['build'].append(dep)
                    categorized = True
                    break

        if not categorized:
            for pattern in lint_patterns:
                if pattern in dep_lower:
                    categories['lint'].append(dep)
                    categorized = True
                    break

        if not categorized:
            if 'util' in dep_lower or 'lodash' in dep_lower or 'ramda' in dep_lower:
                categories['utility'].append(dep)
            else:
                categories['other'].append(dep)

    return {
        'total_deps': len(deps),
        'total_dev_deps': len(dev_deps),
        'categories': categories
    }

def analyze_python_deps(requirements_path='requirements.txt'):
    """Analyze Python dependencies."""
    try:
        with open(requirements_path) as f:
            lines = f.readlines()
    except FileNotFoundError:
        return None

    deps = [line.strip() for line in lines if line.strip() and not line.startswith('#')]

    categories = {
        'web': [],
        'database': [],
        'testing': [],
        'data': [],
        'utility': [],
        'other': []
    }

    web_patterns = ['flask', 'django', 'fastapi', 'tornado', 'quart']
    db_patterns = ['sqlalchemy', 'django-orm', 'peewee', 'pymongo', 'redis', 'psycopg']
    test_patterns = ['pytest', 'unittest', 'mock', 'coverage', 'hypothesis']
    data_patterns = ['pandas', 'numpy', 'scipy', 'matplotlib', 'scikit', 'tensorflow', 'torch']

    for dep in deps:
        dep_lower = dep.lower().split('==')[0].split('>=')[0].split('<')[0]
        categorized = False

        for pattern in web_patterns:
            if pattern in dep_lower:
                categories['web'].append(dep)
                categorized = True
                break

        if not categorized:
            for pattern in db_patterns:
                if pattern in dep_lower:
                    categories['database'].append(dep)
                    categorized = True
                    break

        if not categorized:
            for pattern in test_patterns:
                if pattern in dep_lower:
                    categories['testing'].append(dep)
                    categorized = True
                    break

        if not categorized:
            for pattern in data_patterns:
                if pattern in dep_lower:
                    categories['data'].append(dep)
                    categorized = True
                    break

        if not categorized:
            if 'util' in dep_lower or 'python-' in dep_lower:
                categories['utility'].append(dep)
            else:
                categories['other'].append(dep)

    return {
        'total_deps': len(deps),
        'categories': categories
    }

def print_report(result, project_type):
    """Print formatted dependency report."""
    if not result:
        print(f"No {project_type} dependencies found.")
        return

    print(f"\n{'='*50}")
    print(f"Dependency Analysis: {project_type}")
    print('='*50)

    if 'total_deps' in result:
        print(f"\nTotal Dependencies: {result['total_deps']}")
    if 'total_dev_deps' in result:
        print(f"Dev Dependencies: {result['total_dev_deps']}")

    print("\nCategorized Dependencies:")
    print("-" * 30)

    for category, deps in result['categories'].items():
        if deps:
            print(f"\n{category.upper()}:")
            for dep in deps[:10]:  # Show first 10
                print(f"  • {dep}")
            if len(deps) > 10:
                print(f"  ... and {len(deps) - 10} more")

def main():
    """Main entry point."""
    # Check for Node.js project
    if Path('package.json').exists():
        result = analyze_node_deps()
        print_report(result, "Node.js")

    # Check for Python project
    if Path('requirements.txt').exists():
        result = analyze_python_deps()
        print_report(result, "Python")

    # Check for pyproject.toml
    if Path('pyproject.toml').exists():
        print("\nNote: pyproject.toml detected. Run 'pip list' for full dependency list.")

if __name__ == "__main__":
    main()
