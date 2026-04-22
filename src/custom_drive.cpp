#include <gz/sim/System.hh>
#include <gz/sim/Model.hh>
#include <gz/sim/components/Joint.hh>
#include <gz/sim/components/JointVelocityCmd.hh>
#include <gz/plugin/Register.hh>
#include <gz/transport/Node.hh>
#include <gz/msgs/twist.pb.h>
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
            right_joint_ent = model.JointByName(_ecm,"right_wheel_base");

            node.Subscribe("/cmd_vel",&CustomDrive::OnCmdVel,this);

            std::cout << "\n=======================================\n";
            std::cout <<  "CUSTOM BRAIN ONLINE : Listening for movement commands!";
            std::cout << "\n=======================================\n";
        }

        void PreUpdate(const gz::sim::UpdateInfo &_info,
                       gz::sim::EntityComponentManager &_ecm) override
        {
            if (_info.paused) return;

            double v,w;
            {
                std::lock_guard<std::mutex> lock(msg_mutex);
                v = target_v;
                w = target_w;

            }
            double wheel_separation = 0.64;
            double wheel_radius = 0.2;
            double v_left = (v - (w * wheel_separation / 2.0)) / wheel_radius;
            double v_right = -1.0 *(v + (w * wheel_separation / 2.0)) / wheel_radius;

            std::vector<double> left_cmd = {v_left};
            std::vector<double> right_cmd = {v_right};

            _ecm.SetComponentData<gz::sim::components::JointVelocityCmd>(left_joint_ent, left_cmd);
          _ecm.SetComponentData<gz::sim::components::JointVelocityCmd>(right_joint_ent, right_cmd);
            
        }
    };
}
 GZ_ADD_PLUGIN(my_robot::CustomDrive,
gz::sim::System,
my_robot::CustomDrive::ISystemConfigure,
my_robot::CustomDrive::ISystemPreUpdate)
GZ_ADD_PLUGIN_ALIAS(my_robot::CustomDrive, "my_robot::CustomDrive")