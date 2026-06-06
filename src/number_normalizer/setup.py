from setuptools import find_packages, setup

package_name = 'number_normalizer'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='you@example.com',
    description='MinMaxScaler normalization action server and client',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'normalize_server = number_normalizer.normalize_server:main',
            'normalize_client = number_normalizer.normalize_client:main',
        ],
    },
)
