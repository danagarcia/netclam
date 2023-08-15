# NetClam | API based ClamAV scanner service
## Building
```
# Control Plane
cd netclam-cp
docker build --tag netclam-cp .

# Data Plane
cd netclam-dp
docker build --tag netclam-dp .
```
## Deploying
```
# Control Plane
helm install netclam ./netclam-cp.tgz

# Data Plane
helm install netclam ./netclam-dp.tgz
```
## Contributing
While there are very few rules to contributing, please remember to keep comments constructive on pull-requests and issues. This is an open source project, some contributors may be learning and are coming from other backgrounds. Stay positive and happy contributing!