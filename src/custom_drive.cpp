#include <gz/sim/System.hh>
#include <gz/sim/Model.hh>
#include <gz/sim/components/Joint.hh>
#include <gz/sim/components/JointsVelocityCmd.hh>
#include <gz/plugin/Register.hh>
#include <gz/transport/Node.hh>
#include <gz/msgs/twist/pb.h>
#include <iostream>
#include <mutex>

namespace my_robot
{
    class CustomDrive : public gz::sim::System,
                        public gz::sim::ISystemConfigure,
                        public gz::sim::ISystemPreUpdate
    {
        private:
            gz::transport::Node node;

            gz::sim::Entity left_joint_ent;
            gz::sim::Entity right_joint_ent;

            double target_v = 0.0;
            double target_w = 0.0;

            std::mutex msg_mutex;
        public:
        void OnCmdVel(const gz::msgs::Twist &_msg)
        {
            std::lock_guard<std::mutex> lock(msg_mutex);
            target_v = _msg.linear().x();
            target_w = _msg.angular().z();
        }
        void Configure(const gz::sim::Entity &_entity,
                       const std::shared_ptr<const sdf::Element> &_sdf,
                        gz::sim::EntityComponentManager &_ecm,
                        gz::sim::EventManager &_eventMgr) override
        {
            gz::sim::Model model(_entity);
            left_joint_ent = model.JointByName(_ecm, "left_wheel_base");
            right_joint_ent = model.JointByName(_ecm,"right_wheel_joint");

            node.Subscribe("/cmd_vel",&CustomDrive::OnCmdVel,this);

            std::cout << "\n=======================================\n";
            std::cout <<  "CUSTOM BRAIN ONLINE : Listening for movement commands!";
            std::cout << "\n=======================================\n";
        }

        void
    }
}