# This script would basically is meant to performing the follwoing tasks. 
# 
# Now spin up a local jenkins server fully so as to make sure that it's working locally
# Also spin that up with stipulated env. variables which would spin that up with the 
# password and etc. 
# Post this I also have to setup a Complete CI/CD Pipeline for this project thorugh jenkins
# into a Repository and hence would be 

Jenkins Docker Image based Server Create and Configure 
- Admin Setup with password 
- Github based Local Intergation for the project
- NodeJS Plugin for trigerring Pipeline based jobs 
- Pipeline Plugin should be installed and configured 

(JENKINS-setup)
--------------------------------------------------------------------
(Ci-CD pipeline setup)

- Now create a custom Jenkins File in the local directory 
- This would involve the Building the latest Docker Image copy of the target NodejS project
- And then the deploy stage of Deploying the latest copy of this Projects Local Docker Image to 
- The Docker  Hub with the latest tag i.e. remove the previous image and update this as the 
- Updated latest image on the docker-hub so that universally anyone could download it
- or save this to the github repository allied to it and then remove this and replace
- it with the latest for the next time. 